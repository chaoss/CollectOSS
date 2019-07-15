-- ----------------------------
CREATE SCHEMA augur_data;
CREATE SCHEMA augur_operations;
CREATE SCHEMA spdx;
-- create the schemas
-- ----------------------------

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA augur_data TO augur;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA augur_data TO augur;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA augur_operations TO augur;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA augur_operations TO augur;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA spdx TO augur;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA spdx TO augur;

-- ----------------------------
-- Sequence structure for chaoss_metric_status_cms_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."chaoss_metric_status_cms_id_seq";
CREATE SEQUENCE "augur_data"."chaoss_metric_status_cms_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25150
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
START 25150
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
START 25150
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
START 25150
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
START 25150
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
START 25150
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
START 25150
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
START 25150
CACHE 1;
ALTER SEQUENCE "augur_data"."contributors_history_cntrb_history_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for issue_assignees_issue_assignee_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."issue_assignees_issue_assignee_id_seq";
CREATE SEQUENCE "augur_data"."issue_assignees_issue_assignee_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25150
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
START 25150
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
START 25150
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
START 25150
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
START 25150
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
START 25150
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
START 25150
CACHE 1;
ALTER SEQUENCE "augur_data"."library_version_library_version_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for message_msg_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."message_msg_id_seq";
CREATE SEQUENCE "augur_data"."message_msg_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25150
CACHE 1;
ALTER SEQUENCE "augur_data"."message_msg_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for platform_pltfrm_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."platform_pltfrm_id_seq";
CREATE SEQUENCE "augur_data"."platform_pltfrm_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25150
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
START 25150
CACHE 1;
ALTER SEQUENCE "augur_data"."pull_request_assignees_pr_assignee_map_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for pull_request_events_pr_event_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."pull_request_events_pr_event_id_seq";
CREATE SEQUENCE "augur_data"."pull_request_events_pr_event_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25150
CACHE 1;
ALTER SEQUENCE "augur_data"."pull_request_events_pr_event_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for pull_request_labels_pr_label_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."pull_request_labels_pr_label_id_seq";
CREATE SEQUENCE "augur_data"."pull_request_labels_pr_label_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25150
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
START 25150
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
START 25150
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
START 25150
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
START 25150
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
START 25150
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
START 25150
CACHE 1;
ALTER SEQUENCE "augur_data"."pull_requests_pull_request_id_seq" OWNER TO "augur";

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
-- Sequence structure for repo_group_insights_rgi_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."repo_group_insights_rgi_id_seq";
CREATE SEQUENCE "augur_data"."repo_group_insights_rgi_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25150
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
START 25150
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
START 25150
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
START 25150
CACHE 1;
ALTER SEQUENCE "augur_data"."repo_info_repo_info_id_seq" OWNER TO "augur";

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
START 25150
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
START 25150
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
START 25150
CACHE 1;
ALTER SEQUENCE "augur_data"."repo_repo_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for repo_stats_rstat_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."repo_stats_rstat_id_seq";
CREATE SEQUENCE "augur_data"."repo_stats_rstat_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25150
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
START 25150
CACHE 1;
ALTER SEQUENCE "augur_data"."repo_test_coverage_repo_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for utility_log_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."utility_log_id_seq";
CREATE SEQUENCE "augur_data"."utility_log_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25150
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
START 25150
CACHE 1;
ALTER SEQUENCE "augur_data"."utility_log_id_seq1" OWNER TO "augur";



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
-- Sequence structure for file_types_file_type_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."file_types_file_type_id_seq";
CREATE SEQUENCE "spdx"."file_types_file_type_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."file_types_file_type_id_seq" OWNER TO "augur";

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
-- Sequence structure for projects_project_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."projects_project_id_seq";
CREATE SEQUENCE "spdx"."projects_project_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."projects_project_id_seq" OWNER TO "augur";

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


CREATE TABLE "augur_data"."analysis_log" (
"repos_id" int4 NOT NULL,
"status" varchar(128) COLLATE "default" NOT NULL,
"date_attempted" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP
)
WITHOUT OIDS;
CREATE INDEX "repos_id" ON "augur_data"."analysis_log" USING btree ("repos_id" "pg_catalog"."int4_ops" ASC NULLS LAST);
ALTER TABLE "augur_data"."analysis_log" OWNER TO "augur";

CREATE TABLE "augur_data"."chaoss_metric_status" (
"cms_id" int8 NOT NULL DEFAULT nextval('augur_data.chaoss_metric_status_cms_id_seq'::regclass),
"cm_group" varchar COLLATE "default",
"cm_source" varchar COLLATE "default",
"cm_type" varchar COLLATE "default",
"cm_backend_status" varchar COLLATE "default",
"cm_frontend_status" varchar COLLATE "default",
"cm_defined" bool,
"cm_api_endpoint_repo" varchar COLLATE "default",
"cm_api_endpoint_rg" varchar COLLATE "default",
"cm_name" varchar COLLATE "default",
"cm_working_group" varchar COLLATE "default",
"cm_working_group_focus_area" varchar COLLATE "default",
"cm_info" json,
"tool_source" varchar COLLATE "default",
"tool_version" varchar COLLATE "default",
"data_source" varchar COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "chaoss_metric_status_pkey" PRIMARY KEY ("cms_id") 
)
WITHOUT OIDS;
ALTER TABLE "augur_data"."chaoss_metric_status" OWNER TO "augur";

CREATE TABLE "augur_data"."commit_comment_ref" (
"cmt_comment_id" int8 NOT NULL DEFAULT nextval('augur_data.commit_comment_ref_cmt_comment_id_seq'::regclass),
"cmt_id" int8 NOT NULL,
"msg_id" int8 NOT NULL,
"user_id" int8 NOT NULL,
"body" text COLLATE "default",
"line" int8,
"position" int8,
"created_at" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
"cmt_comment_src_id" int8 NOT NULL,
"commit_comment_src_node_id" varchar COLLATE "default",
CONSTRAINT "commit_comment_ref_pkey" PRIMARY KEY ("cmt_comment_id") ,
CONSTRAINT "commitcomment" UNIQUE ("cmt_id", "msg_id", "cmt_comment_id")
)
WITHOUT OIDS;
CREATE INDEX "comment_id" ON "augur_data"."commit_comment_ref" USING btree ("cmt_comment_src_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "cmt_comment_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "msg_id" "pg_catalog"."int8_ops" ASC NULLS LAST);
COMMENT ON COLUMN "augur_data"."commit_comment_ref"."cmt_comment_src_id" IS 'For data provenance, we store the source ID if it exists. ';
COMMENT ON COLUMN "augur_data"."commit_comment_ref"."commit_comment_src_node_id" IS 'For data provenance, we store the source node ID if it exists. ';
ALTER TABLE "augur_data"."commit_comment_ref" OWNER TO "augur";

CREATE TABLE "augur_data"."commit_parents" (
"cmt_id" int8 NOT NULL,
"parent_id" int8 NOT NULL DEFAULT nextval('augur_data.commit_parents_parent_id_seq'::regclass),
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "commit_parents_pkey" PRIMARY KEY ("cmt_id", "parent_id") 
)
WITHOUT OIDS;
CREATE INDEX "commit_parents_ibfk_1" ON "augur_data"."commit_parents" USING btree ("cmt_id" "pg_catalog"."int8_ops" ASC NULLS LAST);
CREATE INDEX "commit_parents_ibfk_2" ON "augur_data"."commit_parents" USING btree ("parent_id" "pg_catalog"."int8_ops" ASC NULLS LAST);
ALTER TABLE "augur_data"."commit_parents" OWNER TO "augur";

CREATE TABLE "augur_data"."commits" (
"cmt_id" int8 NOT NULL DEFAULT nextval('augur_data.commits_cmt_id_seq'::regclass),
"repo_id" int8 NOT NULL,
"cmt_commit_hash" varchar(80) COLLATE "default" NOT NULL,
"cmt_author_name" varchar(128) COLLATE "default" NOT NULL,
"cmt_author_raw_email" varchar(128) COLLATE "default" NOT NULL,
"cmt_author_email" varchar(128) COLLATE "default" NOT NULL,
"cmt_author_date" varchar(10) COLLATE "default" NOT NULL,
"cmt_author_affiliation" varchar(128) COLLATE "default" DEFAULT 'NULL'::character varying,
"cmt_committer_name" varchar(128) COLLATE "default" NOT NULL,
"cmt_committer_raw_email" varchar(128) COLLATE "default" NOT NULL,
"cmt_committer_email" varchar(128) COLLATE "default" NOT NULL,
"cmt_committer_date" varchar(10) COLLATE "default" NOT NULL,
"cmt_committer_affiliation" varchar(128) COLLATE "default" DEFAULT 'NULL'::character varying,
"cmt_added" int4 NOT NULL,
"cmt_removed" int4 NOT NULL,
"cmt_whitespace" int4 NOT NULL,
"cmt_filename" varchar(4096) COLLATE "default" NOT NULL,
"cmt_date_attempted" timestamp(0) NOT NULL,
"cmt_ght_author_id" int4,
"cmt_ght_committer_id" int4,
"cmt_ght_committed_at" timestamp(0),
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0),
CONSTRAINT "commits_pkey" PRIMARY KEY ("cmt_id") 
)
WITHOUT OIDS;
CREATE INDEX "author_affiliation" ON "augur_data"."commits" USING btree ("cmt_author_affiliation" "pg_catalog"."text_ops" ASC NULLS LAST);
CREATE INDEX "author_email,author_affiliation,author_date" ON "augur_data"."commits" USING btree ("cmt_author_email" "pg_catalog"."text_ops" ASC NULLS LAST, "cmt_author_affiliation" "pg_catalog"."text_ops" ASC NULLS LAST, "cmt_author_date" "pg_catalog"."text_ops" ASC NULLS LAST);
CREATE INDEX "author_raw_email" ON "augur_data"."commits" USING btree ("cmt_author_raw_email" "pg_catalog"."text_ops" ASC NULLS LAST);
CREATE INDEX "commited" ON "augur_data"."commits" USING btree ("cmt_id" "pg_catalog"."int8_ops" ASC NULLS LAST);
CREATE INDEX "committer_affiliation" ON "augur_data"."commits" USING btree ("cmt_committer_affiliation" "pg_catalog"."text_ops" ASC NULLS LAST);
CREATE INDEX "committer_email,committer_affiliation,committer_date" ON "augur_data"."commits" USING btree ("cmt_committer_email" "pg_catalog"."text_ops" ASC NULLS LAST, "cmt_committer_affiliation" "pg_catalog"."text_ops" ASC NULLS LAST, "cmt_committer_date" "pg_catalog"."text_ops" ASC NULLS LAST);
CREATE INDEX "committer_raw_email" ON "augur_data"."commits" USING btree ("cmt_committer_raw_email" "pg_catalog"."text_ops" ASC NULLS LAST);
CREATE INDEX "repo_id,commit" ON "augur_data"."commits" USING btree ("repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "cmt_commit_hash" "pg_catalog"."text_ops" ASC NULLS LAST);
COMMENT ON TABLE "augur_data"."commits" IS 'Starts with augur.analysis_data table and incorporates GHTorrent commit table attributes if different. 
Cmt_id is from get
The author and committer ID’s are at the bottom of the table and not required for now because we want to focus on the facade schema’s properties over the ghtorrent properties when they are in conflict. ';
ALTER TABLE "augur_data"."commits" OWNER TO "augur";

CREATE TABLE "augur_data"."contributor_affiliations" (
"cntrb_id" int8 NOT NULL,
"ca_id" int8 NOT NULL DEFAULT nextval('augur_data.contributor_affiliations_ca_id_seq'::regclass),
"ca_domain" varchar(64) COLLATE "default" NOT NULL,
"ca_affiliation" varchar(64) COLLATE "default" NOT NULL,
"ca_start_date" date NOT NULL DEFAULT CURRENT_DATE,
"ca_active" int2 NOT NULL DEFAULT 1,
"ca_last_modified" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "contributor_affiliations_pkey" PRIMARY KEY ("ca_id", "cntrb_id") 
)
WITHOUT OIDS;
CREATE INDEX "domain,active" ON "augur_data"."contributor_affiliations" USING btree ("ca_domain" "pg_catalog"."text_ops" ASC NULLS LAST, "ca_active" "pg_catalog"."int2_ops" ASC NULLS LAST);
CREATE UNIQUE INDEX "domain,affiliation,start_date" ON "augur_data"."contributor_affiliations" USING btree ("ca_domain" "pg_catalog"."text_ops" ASC NULLS LAST, "ca_affiliation" "pg_catalog"."text_ops" ASC NULLS LAST, "ca_start_date" "pg_catalog"."date_ops" ASC NULLS LAST);
ALTER TABLE "augur_data"."contributor_affiliations" OWNER TO "augur";

CREATE TABLE "augur_data"."contributors" (
"cntrb_id" int8 NOT NULL DEFAULT nextval('augur_data.contributors_cntrb_id_seq'::regclass),
"cntrb_login" varchar(255) COLLATE "default" NOT NULL,
"cntrb_email" varchar(255) COLLATE "default",
"cntrb_company" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"cntrb_created_at" timestamp(0) NOT NULL,
"cntrb_type" varchar(255) COLLATE "default",
"cntrb_fake" int2 NOT NULL DEFAULT 0,
"cntrb_deleted" int2 NOT NULL DEFAULT 0,
"cntrb_long" numeric(11,8) DEFAULT NULL::numeric,
"cntrb_lat" numeric(10,8) DEFAULT NULL::numeric,
"cntrb_country_code" char(3) COLLATE "default" DEFAULT NULL::bpchar,
"cntrb_state" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"cntrb_city" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"cntrb_location" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"cntrb_canonical" varchar(128) COLLATE "default",
"gh_user_id" int8,
"gh_login" varchar(255) COLLATE "default",
"gh_url" varchar(255) COLLATE "default",
"gh_html_url" varchar(255) COLLATE "default",
"gh_node_id" varchar(255) COLLATE "default",
"gh_avatar_url" varchar(4000) COLLATE "default",
"gh_gravatar_id" varchar(255) COLLATE "default",
"gh_followers_url" varchar(4000) COLLATE "default",
"gh_following_url" varchar(4000) COLLATE "default",
"gh_gists_url" varchar(4000) COLLATE "default",
"gh_starred_url" varchar(4000) COLLATE "default",
"gh_subscriptions_url" varchar(4000) COLLATE "default",
"gh_organizations_url" varchar(4000) COLLATE "default",
"gh_repos_url" varchar(4000) COLLATE "default",
"gh_events_url" varchar(4000) COLLATE "default",
"gh_received_events_url" varchar(4000) COLLATE "default",
"gh_type" varchar(255) COLLATE "default",
"gh_site_admin" varchar(255) COLLATE "default",
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "contributors_pkey" PRIMARY KEY ("cntrb_id") 
)
WITHOUT OIDS;
CREATE INDEX "login" ON "augur_data"."contributors" USING btree ("cntrb_login" "pg_catalog"."text_ops" ASC NULLS LAST);
COMMENT ON TABLE "augur_data"."contributors" IS 'For GitHub, this should be repeated from gh_login. for other systems, it should be that systems login. ';
COMMENT ON COLUMN "augur_data"."contributors"."cntrb_login" IS 'Will be a double population with the same value as gh_login for github, but the local value for other systems. ';
COMMENT ON COLUMN "augur_data"."contributors"."cntrb_email" IS 'This needs to be here for matching contributor ids, which are augur, to the commit information. ';
COMMENT ON COLUMN "augur_data"."contributors"."cntrb_type" IS 'Present in another models. It is not currently used in Augur. ';
COMMENT ON COLUMN "augur_data"."contributors"."gh_login" IS 'populated with the github user name for github originated data. ';
ALTER TABLE "augur_data"."contributors" OWNER TO "augur";

CREATE TABLE "augur_data"."contributors_aliases" (
"cntrb_id" int8 NOT NULL,
"cntrb_a_id" int8 NOT NULL DEFAULT nextval('augur_data.contributors_aliases_cntrb_a_id_seq'::regclass),
"canonical_email" varchar(128) COLLATE "default" NOT NULL,
"alias_email" varchar(128) COLLATE "default" NOT NULL,
"cntrb_active" int2 NOT NULL DEFAULT 1,
"cntrb_last_modified" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0),
CONSTRAINT "contributors_aliases_pkey" PRIMARY KEY ("cntrb_id", "cntrb_a_id") 
)
WITHOUT OIDS;
CREATE INDEX "alias,active" ON "augur_data"."contributors_aliases" USING btree ("alias_email" "pg_catalog"."text_ops" ASC NULLS LAST, "cntrb_active" "pg_catalog"."int2_ops" ASC NULLS LAST);
CREATE UNIQUE INDEX "canonical,alias" ON "augur_data"."contributors_aliases" USING btree ("canonical_email" "pg_catalog"."text_ops" ASC NULLS LAST, "alias_email" "pg_catalog"."text_ops" ASC NULLS LAST);
COMMENT ON TABLE "augur_data"."contributors_aliases" IS 'An alias will need to be created for every contributor in this model, otherwise we will have to look in 2 places. ';
ALTER TABLE "augur_data"."contributors_aliases" OWNER TO "augur";

CREATE TABLE "augur_data"."contributors_history" (
"cntrb_history_id" int8 NOT NULL DEFAULT nextval('augur_data.contributors_history_cntrb_history_id_seq'::regclass),
"cntrb_id" int8 NOT NULL,
"cntrb_history_timestamp" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
"cntrb_history_current_bool" bool,
"cntrb_organizations_list" json,
"cntrb_gists_count" int8,
"cntrb_starred_count" int8,
"cntrb_following_count" int8,
"cntrb_follower_count" int8,
"cntrb_login" varchar(255) COLLATE "default" NOT NULL,
"cntrb_email" varchar(255) COLLATE "default",
"cntrb_company" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"cntrb_created_at" timestamp(0) NOT NULL,
"cntrb_type" varchar(255) COLLATE "default",
"cntrb_fake" int2 NOT NULL DEFAULT 0,
"cntrb_deleted" int2 NOT NULL DEFAULT 0,
"cntrb_long" numeric(11,8) DEFAULT NULL::numeric,
"cntrb_lat" numeric(10,8) DEFAULT NULL::numeric,
"cntrb_country_code" char(3) COLLATE "default" DEFAULT NULL::bpchar,
"cntrb_state" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"cntrb_city" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"cntrb_location" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"cntrb_canonical" varchar(128) COLLATE "default",
"gh_user_id" int8,
"gh_login" varchar(255) COLLATE "default",
"gh_url" varchar(255) COLLATE "default",
"gh_html_url" varchar(255) COLLATE "default",
"gh_node_id" varchar(255) COLLATE "default",
"gh_avatar_url" varchar(4000) COLLATE "default",
"gh_gravatar_id" varchar(255) COLLATE "default",
"gh_followers_url" varchar(4000) COLLATE "default",
"gh_following_url" varchar(4000) COLLATE "default",
"gh_gists_url" varchar(4000) COLLATE "default",
"gh_starred_url" varchar(4000) COLLATE "default",
"gh_subscriptions_url" varchar(4000) COLLATE "default",
"gh_organizations_url" varchar(4000) COLLATE "default",
"gh_repos_url" varchar(4000) COLLATE "default",
"gh_events_url" varchar(4000) COLLATE "default",
"gh_received_events_url" varchar(4000) COLLATE "default",
"gh_type" varchar(255) COLLATE "default",
"gh_site_admin" varchar(255) COLLATE "default",
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "contributors_history_pkey" PRIMARY KEY ("cntrb_history_id") 
)
WITHOUT OIDS;
CREATE INDEX "login_index_2" ON "augur_data"."contributors_history" USING btree ("cntrb_login" "pg_catalog"."text_ops" ASC NULLS LAST);
COMMENT ON TABLE "augur_data"."contributors_history" IS 'For GitHub, this should be repeated from gh_login. for other systems, it should be that systems login. ';
COMMENT ON COLUMN "augur_data"."contributors_history"."cntrb_history_current_bool" IS 'At some point it would be great to have a boolean updated by a contributor worker that set the most recent contributor data to true. ';
COMMENT ON COLUMN "augur_data"."contributors_history"."cntrb_login" IS 'Will be a double population with the same value as gh_login for github, but the local value for other systems. ';
COMMENT ON COLUMN "augur_data"."contributors_history"."cntrb_email" IS 'This needs to be here for matching contributor ids, which are augur, to the commit information. ';
COMMENT ON COLUMN "augur_data"."contributors_history"."cntrb_type" IS 'Present in another models. It is not currently used in Augur. ';
COMMENT ON COLUMN "augur_data"."contributors_history"."gh_login" IS 'populated with the github user name for github originated data. ';
ALTER TABLE "augur_data"."contributors_history" OWNER TO "augur";

CREATE TABLE "augur_data"."dm_repo_annual" (
"repo_id" int8 NOT NULL,
"email" varchar(128) COLLATE "default" NOT NULL,
"affiliation" varchar(128) COLLATE "default" DEFAULT 'NULL'::character varying,
"year" int2 NOT NULL,
"added" int8 NOT NULL,
"removed" int8 NOT NULL,
"whitespace" int8 NOT NULL,
"files" int8 NOT NULL,
"patches" int8 NOT NULL,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP
)
WITHOUT OIDS;
CREATE INDEX "repo_id,affiliation_copy_1" ON "augur_data"."dm_repo_annual" USING btree ("repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "affiliation" "pg_catalog"."text_ops" ASC NULLS LAST);
CREATE INDEX "repo_id,email_copy_1" ON "augur_data"."dm_repo_annual" USING btree ("repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "email" "pg_catalog"."text_ops" ASC NULLS LAST);
ALTER TABLE "augur_data"."dm_repo_annual" OWNER TO "augur";

CREATE TABLE "augur_data"."dm_repo_group_annual" (
"repo_group_id" int8 NOT NULL,
"email" varchar(128) COLLATE "default" NOT NULL,
"affiliation" varchar(128) COLLATE "default" DEFAULT 'NULL'::character varying,
"year" int2 NOT NULL,
"added" int8 NOT NULL,
"removed" int8 NOT NULL,
"whitespace" int8 NOT NULL,
"files" int8 NOT NULL,
"patches" int8 NOT NULL,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP
)
WITHOUT OIDS;
CREATE INDEX "projects_id,affiliation_copy_1" ON "augur_data"."dm_repo_group_annual" USING btree ("repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "affiliation" "pg_catalog"."text_ops" ASC NULLS LAST);
CREATE INDEX "projects_id,email_copy_1" ON "augur_data"."dm_repo_group_annual" USING btree ("repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "email" "pg_catalog"."text_ops" ASC NULLS LAST);
ALTER TABLE "augur_data"."dm_repo_group_annual" OWNER TO "augur";

CREATE TABLE "augur_data"."dm_repo_group_monthly" (
"repo_group_id" int8 NOT NULL,
"email" varchar(128) COLLATE "default" NOT NULL,
"affiliation" varchar(128) COLLATE "default" DEFAULT 'NULL'::character varying,
"month" int2 NOT NULL,
"year" int2 NOT NULL,
"added" int8 NOT NULL,
"removed" int8 NOT NULL,
"whitespace" int8 NOT NULL,
"files" int8 NOT NULL,
"patches" int8 NOT NULL,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP
)
WITHOUT OIDS;
CREATE INDEX "projects_id,affiliation_copy_2" ON "augur_data"."dm_repo_group_monthly" USING btree ("repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "affiliation" "pg_catalog"."text_ops" ASC NULLS LAST);
CREATE INDEX "projects_id,email_copy_2" ON "augur_data"."dm_repo_group_monthly" USING btree ("repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "email" "pg_catalog"."text_ops" ASC NULLS LAST);
CREATE INDEX "projects_id,year,affiliation_copy_1" ON "augur_data"."dm_repo_group_monthly" USING btree ("repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "year" "pg_catalog"."int2_ops" ASC NULLS LAST, "affiliation" "pg_catalog"."text_ops" ASC NULLS LAST);
CREATE INDEX "projects_id,year,email_copy_1" ON "augur_data"."dm_repo_group_monthly" USING btree ("repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "year" "pg_catalog"."int2_ops" ASC NULLS LAST, "email" "pg_catalog"."text_ops" ASC NULLS LAST);
ALTER TABLE "augur_data"."dm_repo_group_monthly" OWNER TO "augur";

CREATE TABLE "augur_data"."dm_repo_group_weekly" (
"repo_group_id" int8 NOT NULL,
"email" varchar(128) COLLATE "default" NOT NULL,
"affiliation" varchar(128) COLLATE "default" DEFAULT 'NULL'::character varying,
"week" int2 NOT NULL,
"year" int2 NOT NULL,
"added" int8 NOT NULL,
"removed" int8 NOT NULL,
"whitespace" int8 NOT NULL,
"files" int8 NOT NULL,
"patches" int8 NOT NULL,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP
)
WITHOUT OIDS;
CREATE INDEX "projects_id,affiliation" ON "augur_data"."dm_repo_group_weekly" USING btree ("repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "affiliation" "pg_catalog"."text_ops" ASC NULLS LAST);
CREATE INDEX "projects_id,email" ON "augur_data"."dm_repo_group_weekly" USING btree ("repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "email" "pg_catalog"."text_ops" ASC NULLS LAST);
CREATE INDEX "projects_id,year,affiliation" ON "augur_data"."dm_repo_group_weekly" USING btree ("repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "year" "pg_catalog"."int2_ops" ASC NULLS LAST, "affiliation" "pg_catalog"."text_ops" ASC NULLS LAST);
CREATE INDEX "projects_id,year,email" ON "augur_data"."dm_repo_group_weekly" USING btree ("repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "year" "pg_catalog"."int2_ops" ASC NULLS LAST, "email" "pg_catalog"."text_ops" ASC NULLS LAST);
ALTER TABLE "augur_data"."dm_repo_group_weekly" OWNER TO "augur";

CREATE TABLE "augur_data"."dm_repo_monthly" (
"repo_id" int8 NOT NULL,
"email" varchar(128) COLLATE "default" NOT NULL,
"affiliation" varchar(128) COLLATE "default" DEFAULT 'NULL'::character varying,
"month" int2 NOT NULL,
"year" int2 NOT NULL,
"added" int8 NOT NULL,
"removed" int8 NOT NULL,
"whitespace" int8 NOT NULL,
"files" int8 NOT NULL,
"patches" int8 NOT NULL,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP
)
WITHOUT OIDS;
CREATE INDEX "repo_id,affiliation_copy_2" ON "augur_data"."dm_repo_monthly" USING btree ("repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "affiliation" "pg_catalog"."text_ops" ASC NULLS LAST);
CREATE INDEX "repo_id,email_copy_2" ON "augur_data"."dm_repo_monthly" USING btree ("repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "email" "pg_catalog"."text_ops" ASC NULLS LAST);
CREATE INDEX "repo_id,year,affiliation_copy_1" ON "augur_data"."dm_repo_monthly" USING btree ("repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "year" "pg_catalog"."int2_ops" ASC NULLS LAST, "affiliation" "pg_catalog"."text_ops" ASC NULLS LAST);
CREATE INDEX "repo_id,year,email_copy_1" ON "augur_data"."dm_repo_monthly" USING btree ("repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "year" "pg_catalog"."int2_ops" ASC NULLS LAST, "email" "pg_catalog"."text_ops" ASC NULLS LAST);
ALTER TABLE "augur_data"."dm_repo_monthly" OWNER TO "augur";

CREATE TABLE "augur_data"."dm_repo_weekly" (
"repo_id" int8 NOT NULL,
"email" varchar(128) COLLATE "default" NOT NULL,
"affiliation" varchar(128) COLLATE "default" DEFAULT 'NULL'::character varying,
"week" int2 NOT NULL,
"year" int2 NOT NULL,
"added" int8 NOT NULL,
"removed" int8 NOT NULL,
"whitespace" int8 NOT NULL,
"files" int8 NOT NULL,
"patches" int8 NOT NULL,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP
)
WITHOUT OIDS;
CREATE INDEX "repo_id,affiliation" ON "augur_data"."dm_repo_weekly" USING btree ("repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "affiliation" "pg_catalog"."text_ops" ASC NULLS LAST);
CREATE INDEX "repo_id,email" ON "augur_data"."dm_repo_weekly" USING btree ("repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "email" "pg_catalog"."text_ops" ASC NULLS LAST);
CREATE INDEX "repo_id,year,affiliation" ON "augur_data"."dm_repo_weekly" USING btree ("repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "year" "pg_catalog"."int2_ops" ASC NULLS LAST, "affiliation" "pg_catalog"."text_ops" ASC NULLS LAST);
CREATE INDEX "repo_id,year,email" ON "augur_data"."dm_repo_weekly" USING btree ("repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "year" "pg_catalog"."int2_ops" ASC NULLS LAST, "email" "pg_catalog"."text_ops" ASC NULLS LAST);
ALTER TABLE "augur_data"."dm_repo_weekly" OWNER TO "augur";

CREATE TABLE "augur_data"."exclude" (
"id" int4 NOT NULL,
"projects_id" int4 NOT NULL,
"email" varchar(128) COLLATE "default" DEFAULT 'NULL'::character varying,
"domain" varchar(128) COLLATE "default" DEFAULT 'NULL'::character varying,
CONSTRAINT "exclude_pkey" PRIMARY KEY ("id") 
)
WITHOUT OIDS;
ALTER TABLE "augur_data"."exclude" OWNER TO "augur";

CREATE TABLE "augur_data"."issue_assignees" (
"issue_assignee_id" int8 NOT NULL DEFAULT nextval('augur_data.issue_assignees_issue_assignee_id_seq'::regclass),
"issue_id" int8,
"cntrb_id" int8,
"issue_assignee_src_id" int8,
"issue_assignee_src_node" varchar COLLATE "default",
"tool_source" varchar COLLATE "default",
"tool_version" varchar COLLATE "default",
"data_source" varchar COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "issue_assignees_pkey" PRIMARY KEY ("issue_assignee_id") 
)
WITHOUT OIDS;
COMMENT ON COLUMN "augur_data"."issue_assignees"."issue_assignee_src_id" IS 'This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue events API in the issue_assignees embedded JSON object. We may discover it is an ID for the person themselves; but my hypothesis is that its not.';
COMMENT ON COLUMN "augur_data"."issue_assignees"."issue_assignee_src_node" IS 'This character based identifier comes from the source. In the case of GitHub, it is the id that is the second field returned from the issue events API in the issue_assignees embedded JSON object. We may discover it is an ID for the person themselves; but my hypothesis is that its not.';
ALTER TABLE "augur_data"."issue_assignees" OWNER TO "augur";

CREATE TABLE "augur_data"."issue_events" (
"event_id" int8 NOT NULL DEFAULT nextval('augur_data.issue_events_event_id_seq'::regclass),
"issue_id" int8 NOT NULL,
"cntrb_id" int8 NOT NULL,
"action" varchar(255) COLLATE "default" NOT NULL,
"action_commit_hash" varchar COLLATE "default",
"created_at" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
"issue_event_src_id" int8,
"node_id" varchar COLLATE "default",
"node_url" varchar COLLATE "default",
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "issue_events_pkey" PRIMARY KEY ("event_id") 
)
WITHOUT OIDS;
CREATE INDEX "issue_events_ibfk_1" ON "augur_data"."issue_events" USING btree ("issue_id" "pg_catalog"."int8_ops" ASC NULLS LAST);
CREATE INDEX "issue_events_ibfk_2" ON "augur_data"."issue_events" USING btree ("cntrb_id" "pg_catalog"."int8_ops" ASC NULLS LAST);
COMMENT ON COLUMN "augur_data"."issue_events"."issue_event_src_id" IS 'This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue events API';
COMMENT ON COLUMN "augur_data"."issue_events"."node_id" IS 'This should be renamed to issue_event_src_node_id, as its the varchar identifier in GitHub and likely common in other sources as well. However, since it was created before we came to this naming standard and workers are built around it, we have it simply named as node_id. Anywhere you see node_id in the schema, it comes from GitHubs terminology.';
ALTER TABLE "augur_data"."issue_events" OWNER TO "augur";

CREATE TABLE "augur_data"."issue_labels" (
"issue_label_id" int8 NOT NULL DEFAULT nextval('augur_data.issue_labels_issue_label_id_seq'::regclass),
"issue_id" int8,
"label_text" varchar COLLATE "default",
"label_description" varchar COLLATE "default",
"label_color" varchar COLLATE "default",
"label_src_id" int8,
"label_src_node_id" varchar COLLATE "default",
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "issue_labels_pkey" PRIMARY KEY ("issue_label_id") 
)
WITHOUT OIDS;
COMMENT ON COLUMN "augur_data"."issue_labels"."label_src_id" IS 'This character based identifier (node) comes from the source. In the case of GitHub, it is the id that is the second field returned from the issue events API JSON subsection for issues.';
ALTER TABLE "augur_data"."issue_labels" OWNER TO "augur";

CREATE TABLE "augur_data"."issue_message_ref" (
"issue_msg_ref_id" int8 NOT NULL DEFAULT nextval('augur_data.issue_message_ref_issue_msg_ref_id_seq'::regclass),
"issue_id" int8,
"msg_id" int8,
"issue_msg_ref_src_comment_id" int8,
"issue_msg_ref_src_node_id" varchar COLLATE "default",
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "issue_message_ref_pkey" PRIMARY KEY ("issue_msg_ref_id") 
)
WITHOUT OIDS;
COMMENT ON COLUMN "augur_data"."issue_message_ref"."issue_msg_ref_src_comment_id" IS 'This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue comments API';
COMMENT ON COLUMN "augur_data"."issue_message_ref"."issue_msg_ref_src_node_id" IS 'This character based identifier comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue comments API';
ALTER TABLE "augur_data"."issue_message_ref" OWNER TO "augur";

CREATE TABLE "augur_data"."issues" (
"issue_id" int8 NOT NULL DEFAULT nextval('augur_data.issue_seq'::regclass),
"repo_id" int8,
"reporter_id" int8,
"pull_request" int8,
"pull_request_id" int8,
"created_at" timestamp(0),
"issue_title" varchar(500) COLLATE "default",
"issue_body" text COLLATE "default",
"cntrb_id" int8,
"comment_count" int8,
"updated_at" timestamp(0),
"closed_at" timestamp(0),
"due_on" timestamp(0),
"repository_url" varchar(4000) COLLATE "default",
"issue_url" varchar(4000) COLLATE "default",
"labels_url" varchar(4000) COLLATE "default",
"comments_url" varchar(4000) COLLATE "default",
"events_url" varchar(4000) COLLATE "default",
"html_url" varchar(4000) COLLATE "default",
"issue_state" varchar(255) COLLATE "default",
"issue_node_id" varchar COLLATE "default",
"gh_issue_id" int8,
"gh_user_id" int8,
"gh_issue_number" int8,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "issues_pkey" PRIMARY KEY ("issue_id") 
)
WITHOUT OIDS;
CREATE INDEX "issues_ibfk_1" ON "augur_data"."issues" USING btree ("repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST);
CREATE INDEX "issues_ibfk_2" ON "augur_data"."issues" USING btree ("reporter_id" "pg_catalog"."int8_ops" ASC NULLS LAST);
CREATE INDEX "issues_ibfk_4" ON "augur_data"."issues" USING btree ("pull_request_id" "pg_catalog"."int8_ops" ASC NULLS LAST);
COMMENT ON COLUMN "augur_data"."issues"."reporter_id" IS 'The ID of the person who opened the issue. ';
COMMENT ON COLUMN "augur_data"."issues"."cntrb_id" IS 'The ID of the person who closed the issue. ';
ALTER TABLE "augur_data"."issues" OWNER TO "augur";

CREATE TABLE "augur_data"."libraries" (
"library_id" int8 NOT NULL DEFAULT nextval('augur_data.libraries_library_id_seq'::regclass),
"repo_id" int8,
"platform" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"name" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"created_timestamp" timestamp(0) DEFAULT NULL::timestamp without time zone,
"updated_timestamp" timestamp(0) DEFAULT NULL::timestamp without time zone,
"library_description" varchar(2000) COLLATE "default" DEFAULT NULL::character varying,
"keywords" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"library_homepage" varchar(1000) COLLATE "default" DEFAULT NULL::character varying,
"license" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"version_count" int4,
"latest_release_timestamp" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"latest_release_number" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"package_manager_id" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"dependency_count" int4,
"dependent_library_count" int4,
"primary_language" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0),
CONSTRAINT "libraries_pkey" PRIMARY KEY ("library_id") 
)
WITHOUT OIDS;
ALTER TABLE "augur_data"."libraries" OWNER TO "augur";

CREATE TABLE "augur_data"."library_dependencies" (
"lib_dependency_id" int8 NOT NULL DEFAULT nextval('augur_data.library_dependencies_lib_dependency_id_seq'::regclass),
"library_id" int8,
"manifest_platform" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"manifest_filepath" varchar(1000) COLLATE "default" DEFAULT NULL::character varying,
"manifest_kind" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"repo_id_branch" varchar(255) COLLATE "default" NOT NULL,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0),
CONSTRAINT "library_dependencies_pkey" PRIMARY KEY ("lib_dependency_id") 
)
WITHOUT OIDS;
CREATE INDEX "REPO_DEP" ON "augur_data"."library_dependencies" USING btree ("library_id" "pg_catalog"."int8_ops" ASC NULLS LAST);
ALTER TABLE "augur_data"."library_dependencies" OWNER TO "augur";

CREATE TABLE "augur_data"."library_version" (
"library_version_id" int8 NOT NULL DEFAULT nextval('augur_data.library_version_library_version_id_seq'::regclass),
"library_id" int8,
"library_platform" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"version_number" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"version_release_date" timestamp(0) DEFAULT NULL::timestamp without time zone,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0),
CONSTRAINT "library_version_pkey" PRIMARY KEY ("library_version_id") 
)
WITHOUT OIDS;
ALTER TABLE "augur_data"."library_version" OWNER TO "augur";

CREATE TABLE "augur_data"."message" (
"msg_id" int8 NOT NULL DEFAULT nextval('augur_data.message_msg_id_seq'::regclass),
"rgls_id" int8,
"msg_text" text COLLATE "default",
"msg_timestamp" timestamp(0),
"msg_sender_email" varchar(255) COLLATE "default",
"msg_header" varchar(4000) COLLATE "default",
"pltfrm_id" int8 NOT NULL,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0),
"cntrb_id" int8,
CONSTRAINT "message_pkey" PRIMARY KEY ("msg_id") ,
CONSTRAINT "REPOGROUPLISTER" UNIQUE ("msg_id", "rgls_id"),
CONSTRAINT "platformer" UNIQUE ("msg_id", "pltfrm_id")
)
WITHOUT OIDS;
CREATE UNIQUE INDEX "messagegrouper" ON "augur_data"."message" USING btree ("msg_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "rgls_id" "pg_catalog"."int8_ops" ASC NULLS LAST);
CREATE INDEX "platformgrouper" ON "augur_data"."message" USING btree ("msg_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "pltfrm_id" "pg_catalog"."int8_ops" ASC NULLS LAST);
COMMENT ON COLUMN "augur_data"."message"."cntrb_id" IS 'Not populated for mailing lists. Populated for GitHub issues. ';
ALTER TABLE "augur_data"."message" OWNER TO "augur";

CREATE TABLE "augur_data"."platform" (
"pltfrm_id" int8 NOT NULL DEFAULT nextval('augur_data.platform_pltfrm_id_seq'::regclass),
"pltfrm_name" varchar(255) COLLATE "default",
"pltfrm_version" varchar(255) COLLATE "default",
"pltfrm_release_date" date,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0),
CONSTRAINT "theplat" PRIMARY KEY ("pltfrm_id") 
)
WITHOUT OIDS;
CREATE UNIQUE INDEX "plat" ON "augur_data"."platform" USING btree ("pltfrm_id" "pg_catalog"."int8_ops" ASC NULLS LAST);
ALTER TABLE "augur_data"."platform" OWNER TO "augur";

CREATE TABLE "augur_data"."pull_request_assignees" (
"pr_assignee_map_id" int8 NOT NULL DEFAULT nextval('augur_data.pull_request_assignees_pr_assignee_map_id_seq'::regclass),
"pull_request_id" int8,
"contrib_id" int8,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "pull_request_assignees_pkey" PRIMARY KEY ("pr_assignee_map_id") 
)
WITHOUT OIDS;
ALTER TABLE "augur_data"."pull_request_assignees" OWNER TO "augur";

CREATE TABLE "augur_data"."pull_request_events" (
"pr_event_id" int8 NOT NULL DEFAULT nextval('augur_data.pull_request_events_pr_event_id_seq'::regclass),
"pull_request_id" int8 NOT NULL,
"cntrb_id" int8 NOT NULL,
"action" varchar(255) COLLATE "default" NOT NULL,
"action_commit_hash" varchar COLLATE "default",
"created_at" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
"issue_event_src_id" int8,
"node_id" varchar COLLATE "default",
"node_url" varchar COLLATE "default",
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "pr_events_pkey" PRIMARY KEY ("pr_event_id") 
)
WITHOUT OIDS;
CREATE INDEX "pr_events_ibfk_1" ON "augur_data"."pull_request_events" USING btree ("pull_request_id" "pg_catalog"."int8_ops" ASC NULLS LAST);
CREATE INDEX "pr_events_ibfk_2" ON "augur_data"."pull_request_events" USING btree ("cntrb_id" "pg_catalog"."int8_ops" ASC NULLS LAST);
COMMENT ON COLUMN "augur_data"."pull_request_events"."issue_event_src_id" IS 'This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue events API';
COMMENT ON COLUMN "augur_data"."pull_request_events"."node_id" IS 'This should be renamed to issue_event_src_node_id, as its the varchar identifier in GitHub and likely common in other sources as well. However, since it was created before we came to this naming standard and workers are built around it, we have it simply named as node_id. Anywhere you see node_id in the schema, it comes from GitHubs terminology.';
ALTER TABLE "augur_data"."pull_request_events" OWNER TO "augur";

CREATE TABLE "augur_data"."pull_request_labels" (
"pr_label_id" int8 NOT NULL DEFAULT nextval('augur_data.pull_request_labels_pr_label_id_seq'::regclass),
"pull_request_id" int8,
"pr_src_id" int8,
"pr_src_node_id" varchar COLLATE "default",
"pr_src_url" varchar COLLATE "default",
"pr_src_description" varchar COLLATE "default",
"pr_src_color" varchar COLLATE "default",
"pr_src_default_bool" bool,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "pull_request_labels_pkey" PRIMARY KEY ("pr_label_id") 
)
WITHOUT OIDS;
ALTER TABLE "augur_data"."pull_request_labels" OWNER TO "augur";

CREATE TABLE "augur_data"."pull_request_message_ref" (
"pr_msg_ref_id" int8 NOT NULL DEFAULT nextval('augur_data.pull_request_message_ref_pr_msg_ref_id_seq'::regclass),
"pull_request_id" int8,
"msg_id" int8,
"pr_message_ref_src_comment_id" int8,
"pr_message_ref_src_node_id" varchar COLLATE "default",
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "pull_request_message_ref_pkey" PRIMARY KEY ("pr_msg_ref_id") 
)
WITHOUT OIDS;
ALTER TABLE "augur_data"."pull_request_message_ref" OWNER TO "augur";

CREATE TABLE "augur_data"."pull_request_meta" (
"pr_repo_meta_id" int8 NOT NULL DEFAULT nextval('augur_data.pull_request_meta_pr_repo_meta_id_seq'::regclass),
"pull_request_id" int8,
"pr_head_or_base" varchar COLLATE "default",
"pr_src_meta_label" varchar COLLATE "default",
"pr_src_meta_ref" varchar COLLATE "default",
"pr_sha" varchar COLLATE "default",
"cntrb_id" int8,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "pull_request_meta_pkey" PRIMARY KEY ("pr_repo_meta_id") 
)
WITHOUT OIDS;
COMMENT ON TABLE "augur_data"."pull_request_meta" IS 'Pull requests contain referencing metadata.  There are a few columns that are discrete. There are also head and base designations for the repo on each side of the pull request. Similar functions exist in GitLab, though the language here is based on GitHub. The JSON Being adapted to as of the development of this schema is here:      "base": {       "label": "chaoss:dev",       "ref": "dev",       "sha": "dc6c6f3947f7dc84ecba3d8bda641ef786e7027d",       "user": {         "login": "chaoss",         "id": 29740296,         "node_id": "MDEyOk9yZ2FuaXphdGlvbjI5NzQwMjk2",         "avatar_url": "https://avatars2.githubusercontent.com/u/29740296?v=4",         "gravatar_id": "",         "url": "https://api.github.com/users/chaoss",         "html_url": "https://github.com/chaoss",         "followers_url": "https://api.github.com/users/chaoss/followers",         "following_url": "https://api.github.com/users/chaoss/following{/other_user}",         "gists_url": "https://api.github.com/users/chaoss/gists{/gist_id}",         "starred_url": "https://api.github.com/users/chaoss/starred{/owner}{/repo}",         "subscriptions_url": "https://api.github.com/users/chaoss/subscriptions",         "organizations_url": "https://api.github.com/users/chaoss/orgs",         "repos_url": "https://api.github.com/users/chaoss/repos",         "events_url": "https://api.github.com/users/chaoss/events{/privacy}",         "received_events_url": "https://api.github.com/users/chaoss/received_events",         "type": "Organization",         "site_admin": false       },       "repo": {         "id": 78134122,         "node_id": "MDEwOlJlcG9zaXRvcnk3ODEzNDEyMg==",         "name": "augur",         "full_name": "chaoss/augur",         "private": false,         "owner": {           "login": "chaoss",           "id": 29740296,           "node_id": "MDEyOk9yZ2FuaXphdGlvbjI5NzQwMjk2",           "avatar_url": "https://avatars2.githubusercontent.com/u/29740296?v=4",           "gravatar_id": "",           "url": "https://api.github.com/users/chaoss",           "html_url": "https://github.com/chaoss",           "followers_url": "https://api.github.com/users/chaoss/followers",           "following_url": "https://api.github.com/users/chaoss/following{/other_user}",           "gists_url": "https://api.github.com/users/chaoss/gists{/gist_id}",           "starred_url": "https://api.github.com/users/chaoss/starred{/owner}{/repo}",           "subscriptions_url": "https://api.github.com/users/chaoss/subscriptions",           "organizations_url": "https://api.github.com/users/chaoss/orgs",           "repos_url": "https://api.github.com/users/chaoss/repos",           "events_url": "https://api.github.com/users/chaoss/events{/privacy}",           "received_events_url": "https://api.github.com/users/chaoss/received_events",           "type": "Organization",           "site_admin": false         }, ';
COMMENT ON COLUMN "augur_data"."pull_request_meta"."pr_head_or_base" IS 'Each pull request should have one and only one head record; and one and only one base record. ';
ALTER TABLE "augur_data"."pull_request_meta" OWNER TO "augur";

CREATE TABLE "augur_data"."pull_request_repo" (
"pr_repo_id" int8 NOT NULL DEFAULT nextval('augur_data.pull_request_repo_pr_repo_id_seq'::regclass),
"pr_repo_meta_id" int8,
"pr_repo_head_or_base" varchar COLLATE "default",
"pr_src_repo_id" int8,
"pr_src_node_id" int8,
"pr_repo_name" varchar COLLATE "default",
"pr_repo_full_name" varchar COLLATE "default",
"pr_repo_private_bool" bool,
"pr_cntrb_id" int8,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "pull_request_repo_pkey" PRIMARY KEY ("pr_repo_id") 
)
WITHOUT OIDS;
COMMENT ON COLUMN "augur_data"."pull_request_repo"."pr_repo_head_or_base" IS 'For ease of validation checking, we should determine if the repository referenced is the head or base of the pull request. Each pull request should have one and only one of these, which is not enforcable easily in the database.';
ALTER TABLE "augur_data"."pull_request_repo" OWNER TO "augur";

CREATE TABLE "augur_data"."pull_request_reviewers" (
"pr_reviewer_map_id" int8 NOT NULL DEFAULT nextval('augur_data.pull_request_reviewers_pr_reviewer_map_id_seq'::regclass),
"pull_request_id" int8,
"cntrb_id" int8,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "pull_request_reviewers_pkey" PRIMARY KEY ("pr_reviewer_map_id") 
)
WITHOUT OIDS;
ALTER TABLE "augur_data"."pull_request_reviewers" OWNER TO "augur";

CREATE TABLE "augur_data"."pull_request_teams" (
"pr_team_id" int8 NOT NULL DEFAULT nextval('augur_data.pull_request_teams_pr_team_id_seq'::regclass),
"pull_request_id" int8,
"pr_src_team_id" int8,
"pr_src_team_node" varchar COLLATE "default",
"pr_src_team_url" varchar COLLATE "default",
"pr_team_name" varchar COLLATE "default",
"pr_team_slug" varchar COLLATE "default",
"pr_team_description" varchar COLLATE "default",
"pr_team_privacy" varchar COLLATE "default",
"pr_team_permission" varchar COLLATE "default",
"pr_team_src_members_url" varchar COLLATE "default",
"pr_team_src_repositories_url" varchar COLLATE "default",
"pr_team_parent_id" int8,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "pull_request_teams_pkey" PRIMARY KEY ("pr_team_id") 
)
WITHOUT OIDS;
ALTER TABLE "augur_data"."pull_request_teams" OWNER TO "augur";

CREATE TABLE "augur_data"."pull_requests" (
"pull_request_id" int8 NOT NULL DEFAULT nextval('augur_data.pull_requests_pull_request_id_seq'::regclass),
"pr_url" varchar COLLATE "default",
"pr_src_id" int8,
"pr_src_node_id" int8,
"pr_html_url" varchar COLLATE "default",
"pr_diff_url" varchar COLLATE "default",
"pr_patch_url" varchar COLLATE "default",
"pr_issue_url" varchar COLLATE "default",
"pr_augur_issue_id" int8,
"pr_src_number" int8,
"pr_src_state" varchar COLLATE "default",
"pr_src_locked" bool,
"pr_src_title" varchar COLLATE "default",
"pr_augur_contributor_id" int8,
"pr_body" text COLLATE "default",
"pr_created_at" timestamp(0),
"pr_updated_at" timestamp(0),
"pr_closed_at" timestamp(0),
"pr_merged_at" timestamp(0),
"pr_merge_commit_sha" varchar COLLATE "default",
"pr_teams" int8,
"pr_milestone" varchar COLLATE "default",
"pr_commits_url" varchar COLLATE "default",
"pr_review_comments_url" varchar COLLATE "default",
"pr_review_comment_url" varchar COLLATE "default",
"pr_comments_url" varchar COLLATE "default",
"pr_statuses_url" varchar COLLATE "default",
"pr_meta_head_id" int8,
"pr_meta_base_id" int8,
"pr_src_issue_url" varchar COLLATE "default",
"pr_src_comments_url" varchar COLLATE "default",
"pr_src_review_comments_url" varchar COLLATE "default",
"pr_src_commits_url" varchar COLLATE "default",
"pr_src_statuses_url" varchar COLLATE "default",
"pr_src_author_association" varchar COLLATE "default",
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "pull_requests_pkey" PRIMARY KEY ("pull_request_id") 
)
WITHOUT OIDS;
CREATE INDEX "id_node" ON "augur_data"."pull_requests" USING btree ("pr_src_id" "pg_catalog"."int8_ops" DESC NULLS FIRST, "pr_src_node_id" "pg_catalog"."int8_ops" DESC NULLS LAST);
COMMENT ON COLUMN "augur_data"."pull_requests"."pr_augur_issue_id" IS 'This is to link to the augur stored related issue';
COMMENT ON COLUMN "augur_data"."pull_requests"."pr_augur_contributor_id" IS 'This is to link to the augur contributor record. ';
COMMENT ON COLUMN "augur_data"."pull_requests"."pr_teams" IS 'One to many with pull request teams. ';
COMMENT ON COLUMN "augur_data"."pull_requests"."pr_review_comment_url" IS 'This is a field with limited utility. It does expose how to access a specific comment if needed with parameters. If the source changes URL structure, it may be useful';
COMMENT ON COLUMN "augur_data"."pull_requests"."pr_meta_head_id" IS 'The metadata for the head repo that links to the pull_request_meta table. ';
COMMENT ON COLUMN "augur_data"."pull_requests"."pr_meta_base_id" IS 'The metadata for the base repo that links to the pull_request_meta table. ';
ALTER TABLE "augur_data"."pull_requests" OWNER TO "augur";

CREATE TABLE "augur_data"."repo" (
"repo_id" int8 NOT NULL DEFAULT nextval('augur_data.repo_repo_id_seq'::regclass),
"repo_group_id" int8 NOT NULL,
"repo_git" varchar(256) COLLATE "default" NOT NULL,
"repo_path" varchar(256) COLLATE "default" DEFAULT 'NULL'::character varying,
"repo_name" varchar(256) COLLATE "default" DEFAULT 'NULL'::character varying,
"repo_added" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
"repo_status" varchar(32) COLLATE "default" NOT NULL,
"repo_type" varchar COLLATE "default" DEFAULT ''::character varying,
"url" varchar(255) COLLATE "default",
"owner_id" int4,
"description" varchar COLLATE "default",
"primary_language" varchar(255) COLLATE "default",
"created_at" varchar(255) COLLATE "default",
"forked_from" int8,
"updated_at" timestamp(0),
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0),
CONSTRAINT "repounique" PRIMARY KEY ("repo_id") 
)
WITHOUT OIDS;
CREATE INDEX "forked" ON "augur_data"."repo" USING btree ("forked_from" "pg_catalog"."int8_ops" ASC NULLS LAST);
CREATE UNIQUE INDEX "therepo" ON "augur_data"."repo" USING btree ("repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST);
COMMENT ON TABLE "augur_data"."repo" IS 'This table is a combination of the columns in Facade’s repo table and GHTorrent’s projects table. ';
COMMENT ON COLUMN "augur_data"."repo"."repo_type" IS 'This field is intended to indicate if the repository is the "main instance" of a repository in cases where implementations choose to add the same repository to more than one repository group. In cases where the repository group is of rg_type Github Organization then this repo_type should be "primary". In other cases the repo_type should probably be "user created". We made this a varchar in order to hold open the possibility that there are additional repo_types we have not thought about. ';
ALTER TABLE "augur_data"."repo" OWNER TO "augur";

CREATE TABLE "augur_data"."repo_badging" (
"badge_collection_id" int8 NOT NULL DEFAULT nextval('augur_data.repo_badging_badge_collection_id_seq'::regclass),
"repo_id" int8,
"id" varchar(4000) COLLATE "default",
"user_id" varchar(4000) COLLATE "default",
"name" varchar(4000) COLLATE "default",
"description" varchar(4000) COLLATE "default",
"homepage_url" varchar(4000) COLLATE "default",
"repo_url" varchar(4000) COLLATE "default",
"license" varchar(4000) COLLATE "default",
"homepage_url_status" varchar(4000) COLLATE "default",
"homepage_url_justification" varchar(4000) COLLATE "default",
"sites_https_status" varchar(4000) COLLATE "default",
"sites_https_justification" varchar(4000) COLLATE "default",
"description_good_status" varchar(4000) COLLATE "default",
"description_good_justification" varchar(4000) COLLATE "default",
"interact_status" varchar(4000) COLLATE "default",
"interact_justification" varchar(4000) COLLATE "default",
"contribution_status" varchar(4000) COLLATE "default",
"contribution_justification" varchar(4000) COLLATE "default",
"contribution_requirements_status" varchar(4000) COLLATE "default",
"contribution_requirements_justification" varchar(4000) COLLATE "default",
"license_location_status" varchar(4000) COLLATE "default",
"license_location_justification" varchar(4000) COLLATE "default",
"floss_license_status" varchar(4000) COLLATE "default",
"floss_license_justification" varchar(4000) COLLATE "default",
"floss_license_osi_status" varchar(4000) COLLATE "default",
"floss_license_osi_justification" varchar(4000) COLLATE "default",
"documentation_basics_status" varchar(4000) COLLATE "default",
"documentation_basics_justification" varchar(4000) COLLATE "default",
"documentation_interface_status" varchar(4000) COLLATE "default",
"documentation_interface_justification" varchar(4000) COLLATE "default",
"repo_public_status" varchar(4000) COLLATE "default",
"repo_public_justification" varchar(4000) COLLATE "default",
"repo_track_status" varchar(4000) COLLATE "default",
"repo_track_justification" varchar(4000) COLLATE "default",
"repo_interim_status" varchar(4000) COLLATE "default",
"repo_interim_justification" varchar(4000) COLLATE "default",
"repo_distributed_status" varchar(4000) COLLATE "default",
"repo_distributed_justification" varchar(4000) COLLATE "default",
"version_unique_status" varchar(4000) COLLATE "default",
"version_unique_justification" varchar(4000) COLLATE "default",
"version_semver_status" varchar(4000) COLLATE "default",
"version_semver_justification" varchar(4000) COLLATE "default",
"version_tags_status" varchar(4000) COLLATE "default",
"version_tags_justification" varchar(4000) COLLATE "default",
"release_notes_status" varchar(4000) COLLATE "default",
"release_notes_justification" varchar(4000) COLLATE "default",
"release_notes_vulns_status" varchar(4000) COLLATE "default",
"release_notes_vulns_justification" varchar(4000) COLLATE "default",
"report_url_status" varchar(4000) COLLATE "default",
"report_url_justification" varchar(4000) COLLATE "default",
"report_tracker_status" varchar(4000) COLLATE "default",
"report_tracker_justification" varchar(4000) COLLATE "default",
"report_process_status" varchar(4000) COLLATE "default",
"report_process_justification" varchar(4000) COLLATE "default",
"report_responses_status" varchar(4000) COLLATE "default",
"report_responses_justification" varchar(4000) COLLATE "default",
"enhancement_responses_status" varchar(4000) COLLATE "default",
"enhancement_responses_justification" varchar(4000) COLLATE "default",
"report_archive_status" varchar(4000) COLLATE "default",
"report_archive_justification" varchar(4000) COLLATE "default",
"vulnerability_report_process_status" varchar(4000) COLLATE "default",
"vulnerability_report_process_justification" varchar(4000) COLLATE "default",
"vulnerability_report_private_status" varchar(4000) COLLATE "default",
"vulnerability_report_private_justification" varchar(4000) COLLATE "default",
"vulnerability_report_response_status" varchar(4000) COLLATE "default",
"vulnerability_report_response_justification" varchar(4000) COLLATE "default",
"build_status" varchar(4000) COLLATE "default",
"build_justification" varchar(4000) COLLATE "default",
"build_common_tools_status" varchar(4000) COLLATE "default",
"build_common_tools_justification" varchar(4000) COLLATE "default",
"build_floss_tools_status" varchar(4000) COLLATE "default",
"build_floss_tools_justification" varchar(4000) COLLATE "default",
"test_status" varchar(4000) COLLATE "default",
"test_justification" varchar(4000) COLLATE "default",
"test_invocation_status" varchar(4000) COLLATE "default",
"test_invocation_justification" varchar(4000) COLLATE "default",
"test_most_status" varchar(4000) COLLATE "default",
"test_most_justification" varchar(4000) COLLATE "default",
"test_policy_status" varchar(4000) COLLATE "default",
"test_policy_justification" varchar(4000) COLLATE "default",
"tests_are_added_status" varchar(4000) COLLATE "default",
"tests_are_added_justification" varchar(4000) COLLATE "default",
"tests_documented_added_status" varchar(4000) COLLATE "default",
"tests_documented_added_justification" varchar(4000) COLLATE "default",
"warnings_status" varchar(4000) COLLATE "default",
"warnings_justification" varchar(4000) COLLATE "default",
"warnings_fixed_status" varchar(4000) COLLATE "default",
"warnings_fixed_justification" varchar(4000) COLLATE "default",
"warnings_strict_status" varchar(4000) COLLATE "default",
"warnings_strict_justification" varchar(4000) COLLATE "default",
"know_secure_design_status" varchar(4000) COLLATE "default",
"know_secure_design_justification" varchar(4000) COLLATE "default",
"know_common_errors_status" varchar(4000) COLLATE "default",
"know_common_errors_justification" varchar(4000) COLLATE "default",
"crypto_published_status" varchar(4000) COLLATE "default",
"crypto_published_justification" varchar(4000) COLLATE "default",
"crypto_call_status" varchar(4000) COLLATE "default",
"crypto_call_justification" varchar(4000) COLLATE "default",
"crypto_floss_status" varchar(4000) COLLATE "default",
"crypto_floss_justification" varchar(4000) COLLATE "default",
"crypto_keylength_status" varchar(4000) COLLATE "default",
"crypto_keylength_justification" varchar(4000) COLLATE "default",
"crypto_working_status" varchar(4000) COLLATE "default",
"crypto_working_justification" varchar(4000) COLLATE "default",
"crypto_pfs_status" varchar(4000) COLLATE "default",
"crypto_pfs_justification" varchar(4000) COLLATE "default",
"crypto_password_storage_status" varchar(4000) COLLATE "default",
"crypto_password_storage_justification" varchar(4000) COLLATE "default",
"crypto_random_status" varchar(4000) COLLATE "default",
"crypto_random_justification" varchar(4000) COLLATE "default",
"delivery_mitm_status" varchar(4000) COLLATE "default",
"delivery_mitm_justification" varchar(4000) COLLATE "default",
"delivery_unsigned_status" varchar(4000) COLLATE "default",
"delivery_unsigned_justification" varchar(4000) COLLATE "default",
"vulnerabilities_fixed_60_days_status" varchar(4000) COLLATE "default",
"vulnerabilities_fixed_60_days_justification" varchar(4000) COLLATE "default",
"vulnerabilities_critical_fixed_status" varchar(4000) COLLATE "default",
"vulnerabilities_critical_fixed_justification" varchar(4000) COLLATE "default",
"static_analysis_status" varchar(4000) COLLATE "default",
"static_analysis_justification" varchar(4000) COLLATE "default",
"static_analysis_common_vulnerabilities_status" varchar(4000) COLLATE "default",
"static_analysis_common_vulnerabilities_justification" varchar(4000) COLLATE "default",
"static_analysis_fixed_status" varchar(4000) COLLATE "default",
"static_analysis_fixed_justification" varchar(4000) COLLATE "default",
"static_analysis_often_status" varchar(4000) COLLATE "default",
"static_analysis_often_justification" varchar(4000) COLLATE "default",
"dynamic_analysis_status" varchar(4000) COLLATE "default",
"dynamic_analysis_justification" varchar(4000) COLLATE "default",
"dynamic_analysis_unsafe_status" varchar(4000) COLLATE "default",
"dynamic_analysis_unsafe_justification" varchar(4000) COLLATE "default",
"dynamic_analysis_enable_assertions_status" varchar(4000) COLLATE "default",
"dynamic_analysis_enable_assertions_justification" varchar(4000) COLLATE "default",
"dynamic_analysis_fixed_status" varchar(4000) COLLATE "default",
"dynamic_analysis_fixed_justification" varchar(4000) COLLATE "default",
"general_comments" varchar(4000) COLLATE "default",
"created_at" varchar(4000) COLLATE "default",
"updated_at" varchar(4000) COLLATE "default",
"crypto_weaknesses_status" varchar(4000) COLLATE "default",
"crypto_weaknesses_justification" varchar(4000) COLLATE "default",
"test_continuous_integration_status" varchar(4000) COLLATE "default",
"test_continuous_integration_justification" varchar(4000) COLLATE "default",
"cpe" varchar(4000) COLLATE "default",
"discussion_status" varchar(4000) COLLATE "default",
"discussion_justification" varchar(4000) COLLATE "default",
"no_leaked_credentials_status" varchar(4000) COLLATE "default",
"no_leaked_credentials_justification" varchar(4000) COLLATE "default",
"english_status" varchar(4000) COLLATE "default",
"english_justification" varchar(4000) COLLATE "default",
"hardening_status" varchar(4000) COLLATE "default",
"hardening_justification" varchar(4000) COLLATE "default",
"crypto_used_network_status" varchar(4000) COLLATE "default",
"crypto_used_network_justification" varchar(4000) COLLATE "default",
"crypto_tls12_status" varchar(4000) COLLATE "default",
"crypto_tls12_justification" varchar(4000) COLLATE "default",
"crypto_certificate_verification_status" varchar(4000) COLLATE "default",
"crypto_certificate_verification_justification" varchar(4000) COLLATE "default",
"crypto_verification_private_status" varchar(4000) COLLATE "default",
"crypto_verification_private_justification" varchar(4000) COLLATE "default",
"hardened_site_status" varchar(4000) COLLATE "default",
"hardened_site_justification" varchar(4000) COLLATE "default",
"installation_common_status" varchar(4000) COLLATE "default",
"installation_common_justification" varchar(4000) COLLATE "default",
"build_reproducible_status" varchar(4000) COLLATE "default",
"build_reproducible_justification" varchar(4000) COLLATE "default",
"badge_percentage_0" varchar(4000) COLLATE "default",
"achieved_passing_at" varchar(4000) COLLATE "default",
"lost_passing_at" varchar(4000) COLLATE "default",
"last_reminder_at" varchar(4000) COLLATE "default",
"disabled_reminders" varchar(4000) COLLATE "default",
"implementation_languages" varchar(4000) COLLATE "default",
"lock_version" varchar(4000) COLLATE "default",
"badge_percentage_1" varchar(4000) COLLATE "default",
"dco_status" varchar(4000) COLLATE "default",
"dco_justification" varchar(4000) COLLATE "default",
"governance_status" varchar(4000) COLLATE "default",
"governance_justification" varchar(4000) COLLATE "default",
"code_of_conduct_status" varchar(4000) COLLATE "default",
"code_of_conduct_justification" varchar(4000) COLLATE "default",
"roles_responsibilities_status" varchar(4000) COLLATE "default",
"roles_responsibilities_justification" varchar(4000) COLLATE "default",
"access_continuity_status" varchar(4000) COLLATE "default",
"access_continuity_justification" varchar(4000) COLLATE "default",
"bus_factor_status" varchar(4000) COLLATE "default",
"bus_factor_justification" varchar(4000) COLLATE "default",
"documentation_roadmap_status" varchar(4000) COLLATE "default",
"documentation_roadmap_justification" varchar(4000) COLLATE "default",
"documentation_architecture_status" varchar(4000) COLLATE "default",
"documentation_architecture_justification" varchar(4000) COLLATE "default",
"documentation_security_status" varchar(4000) COLLATE "default",
"documentation_security_justification" varchar(4000) COLLATE "default",
"documentation_quick_start_status" varchar(4000) COLLATE "default",
"documentation_quick_start_justification" varchar(4000) COLLATE "default",
"documentation_current_status" varchar(4000) COLLATE "default",
"documentation_current_justification" varchar(4000) COLLATE "default",
"documentation_achievements_status" varchar(4000) COLLATE "default",
"documentation_achievements_justification" varchar(4000) COLLATE "default",
"accessibility_best_practices_status" varchar(4000) COLLATE "default",
"accessibility_best_practices_justification" varchar(4000) COLLATE "default",
"internationalization_status" varchar(4000) COLLATE "default",
"internationalization_justification" varchar(4000) COLLATE "default",
"sites_password_security_status" varchar(4000) COLLATE "default",
"sites_password_security_justification" varchar(4000) COLLATE "default",
"maintenance_or_update_status" varchar(4000) COLLATE "default",
"maintenance_or_update_justification" varchar(4000) COLLATE "default",
"vulnerability_report_credit_status" varchar(4000) COLLATE "default",
"vulnerability_report_credit_justification" varchar(4000) COLLATE "default",
"vulnerability_response_process_status" varchar(4000) COLLATE "default",
"vulnerability_response_process_justification" varchar(4000) COLLATE "default",
"coding_standards_status" varchar(4000) COLLATE "default",
"coding_standards_justification" varchar(4000) COLLATE "default",
"coding_standards_enforced_status" varchar(4000) COLLATE "default",
"coding_standards_enforced_justification" varchar(4000) COLLATE "default",
"build_standard_variables_status" varchar(4000) COLLATE "default",
"build_standard_variables_justification" varchar(4000) COLLATE "default",
"build_preserve_debug_status" varchar(4000) COLLATE "default",
"build_preserve_debug_justification" varchar(4000) COLLATE "default",
"build_non_recursive_status" varchar(4000) COLLATE "default",
"build_non_recursive_justification" varchar(4000) COLLATE "default",
"build_repeatable_status" varchar(4000) COLLATE "default",
"build_repeatable_justification" varchar(4000) COLLATE "default",
"installation_standard_variables_status" varchar(4000) COLLATE "default",
"installation_standard_variables_justification" varchar(4000) COLLATE "default",
"installation_development_quick_status" varchar(4000) COLLATE "default",
"installation_development_quick_justification" varchar(4000) COLLATE "default",
"external_dependencies_status" varchar(4000) COLLATE "default",
"external_dependencies_justification" varchar(4000) COLLATE "default",
"dependency_monitoring_status" varchar(4000) COLLATE "default",
"dependency_monitoring_justification" varchar(4000) COLLATE "default",
"updateable_reused_components_status" varchar(4000) COLLATE "default",
"updateable_reused_components_justification" varchar(4000) COLLATE "default",
"interfaces_current_status" varchar(4000) COLLATE "default",
"interfaces_current_justification" varchar(4000) COLLATE "default",
"automated_integration_testing_status" varchar(4000) COLLATE "default",
"automated_integration_testing_justification" varchar(4000) COLLATE "default",
"regression_tests_added50_status" varchar(4000) COLLATE "default",
"regression_tests_added50_justification" varchar(4000) COLLATE "default",
"test_statement_coverage80_status" varchar(4000) COLLATE "default",
"test_statement_coverage80_justification" varchar(4000) COLLATE "default",
"test_policy_mandated_status" varchar(4000) COLLATE "default",
"test_policy_mandated_justification" varchar(4000) COLLATE "default",
"implement_secure_design_status" varchar(4000) COLLATE "default",
"implement_secure_design_justification" varchar(4000) COLLATE "default",
"input_validation_status" varchar(4000) COLLATE "default",
"input_validation_justification" varchar(4000) COLLATE "default",
"crypto_algorithm_agility_status" varchar(4000) COLLATE "default",
"crypto_algorithm_agility_justification" varchar(4000) COLLATE "default",
"crypto_credential_agility_status" varchar(4000) COLLATE "default",
"crypto_credential_agility_justification" varchar(4000) COLLATE "default",
"signed_releases_status" varchar(4000) COLLATE "default",
"signed_releases_justification" varchar(4000) COLLATE "default",
"version_tags_signed_status" varchar(4000) COLLATE "default",
"version_tags_signed_justification" varchar(4000) COLLATE "default",
"badge_percentage_2" varchar(4000) COLLATE "default",
"contributors_unassociated_status" varchar(4000) COLLATE "default",
"contributors_unassociated_justification" varchar(4000) COLLATE "default",
"copyright_per_file_status" varchar(4000) COLLATE "default",
"copyright_per_file_justification" varchar(4000) COLLATE "default",
"license_per_file_status" varchar(4000) COLLATE "default",
"license_per_file_justification" varchar(4000) COLLATE "default",
"small_tasks_status" varchar(4000) COLLATE "default",
"small_tasks_justification" varchar(4000) COLLATE "default",
"require_2FA_status" varchar(4000) COLLATE "default",
"require_2FA_justification" varchar(4000) COLLATE "default",
"secure_2FA_status" varchar(4000) COLLATE "default",
"secure_2FA_justification" varchar(4000) COLLATE "default",
"code_review_standards_status" varchar(4000) COLLATE "default",
"code_review_standards_justification" varchar(4000) COLLATE "default",
"two_person_review_status" varchar(4000) COLLATE "default",
"two_person_review_justification" varchar(4000) COLLATE "default",
"test_statement_coverage90_status" varchar(4000) COLLATE "default",
"test_statement_coverage90_justification" varchar(4000) COLLATE "default",
"test_branch_coverage80_status" varchar(4000) COLLATE "default",
"test_branch_coverage80_justification" varchar(4000) COLLATE "default",
"security_review_status" varchar(4000) COLLATE "default",
"security_review_justification" varchar(4000) COLLATE "default",
"assurance_case_status" varchar(4000) COLLATE "default",
"assurance_case_justification" varchar(4000) COLLATE "default",
"achieve_passing_status" varchar(4000) COLLATE "default",
"achieve_passing_justification" varchar(4000) COLLATE "default",
"achieve_silver_status" varchar(4000) COLLATE "default",
"achieve_silver_justification" varchar(4000) COLLATE "default",
"tiered_percentage" varchar(4000) COLLATE "default",
"badge_level" varchar(4000) COLLATE "default",
"additional_rights" int4[],
"project_entry_license" varchar(4000) COLLATE "default",
"project_entry_attribution" varchar(4000) COLLATE "default",
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "repo_badging_pkey" PRIMARY KEY ("badge_collection_id") 
)
WITHOUT OIDS;
COMMENT ON TABLE "augur_data"."repo_badging" IS 'This will be collected from the LF’s Badging API
https://bestpractices.coreinfrastructure.org/projects.json?pq=https%3A%2F%2Fgithub.com%2Fchaoss%2Faugur
';
ALTER TABLE "augur_data"."repo_badging" OWNER TO "augur";

CREATE TABLE "augur_data"."repo_ghtorrent_map" (
"repo_url" varchar(1000) COLLATE "default" DEFAULT NULL::character varying,
"repo_owner" varchar(400) COLLATE "default",
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0)
)
WITHOUT OIDS;
ALTER TABLE "augur_data"."repo_ghtorrent_map" OWNER TO "augur";

CREATE TABLE "augur_data"."repo_group_insights" (
"rgi_id" int8 NOT NULL DEFAULT nextval('augur_data.repo_group_insights_rgi_id_seq'::regclass),
"repo_group_id" int8,
"rgi_metric" varchar COLLATE "default",
"rgi_value" varchar COLLATE "default",
"cms_id" int8,
"rgi_fresh" bool,
"tool_source" varchar COLLATE "default",
"tool_version" varchar COLLATE "default",
"data_source" varchar COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "repo_group_insights_pkey" PRIMARY KEY ("rgi_id") 
)
WITHOUT OIDS;
COMMENT ON TABLE "augur_data"."repo_group_insights" IS 'This table is output from an analytical worker inside of Augur. It runs through the different metrics on a REPOSITORY_GROUP and identifies the five to ten most “interesting” metrics as defined by some kind of delta or other factor. The algorithm is going to evolve. 

Worker Design Notes: The idea is that the "insight worker" will scan through a bunch of active metrics or "synthetic metrics" to list the most important insights. ';
COMMENT ON COLUMN "augur_data"."repo_group_insights"."rgi_fresh" IS 'false if the date is before the statistic that triggered the insight, true if after. This allows us to automatically display only "fresh insights" and avoid displaying "stale insights". The insight worker will populate this table. ';
ALTER TABLE "augur_data"."repo_group_insights" OWNER TO "augur";

CREATE TABLE "augur_data"."repo_groups" (
"repo_group_id" int8 NOT NULL DEFAULT nextval('augur_data.repo_groups_repo_group_id_seq'::regclass),
"rg_name" varchar(128) COLLATE "default" NOT NULL,
"rg_description" varchar(256) COLLATE "default" DEFAULT 'NULL'::character varying,
"rg_website" varchar(128) COLLATE "default" DEFAULT 'NULL'::character varying,
"rg_recache" int2 DEFAULT 1,
"rg_last_modified" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
"rg_type" varchar COLLATE "default",
"tool_source" varchar(255) COLLATE "default" NOT NULL,
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0),
CONSTRAINT "rgid" PRIMARY KEY ("repo_group_id", "tool_source") 
)
WITHOUT OIDS;
CREATE UNIQUE INDEX "rgidm" ON "augur_data"."repo_groups" USING btree ("repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST);
COMMENT ON TABLE "augur_data"."repo_groups" IS 'rg_type is intended to be either a GitHub Organization or a User Created Repo Group. ';
ALTER TABLE "augur_data"."repo_groups" OWNER TO "augur";

CREATE TABLE "augur_data"."repo_groups_list_serve" (
"rgls_id" int8 NOT NULL DEFAULT nextval('augur_data.repo_groups_list_serve_rgls_id_seq'::regclass),
"repo_group_id" int8 NOT NULL,
"rgls_name" varchar(255) COLLATE "default",
"rgls_description" varchar(3000) COLLATE "default",
"rgls_sponsor" varchar(255) COLLATE "default",
"rgls_email" varchar(255) COLLATE "default",
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0),
CONSTRAINT "repo_groups_list_serve_pkey" PRIMARY KEY ("rgls_id") ,
CONSTRAINT "rglistserve" UNIQUE ("rgls_id", "repo_group_id")
)
WITHOUT OIDS;
CREATE UNIQUE INDEX "lister" ON "augur_data"."repo_groups_list_serve" USING btree ("rgls_id" "pg_catalog"."int8_ops" ASC NULLS LAST, "repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST);
ALTER TABLE "augur_data"."repo_groups_list_serve" OWNER TO "augur";

CREATE TABLE "augur_data"."repo_info" (
"repo_info_id" int8 NOT NULL DEFAULT nextval('augur_data.repo_info_repo_info_id_seq'::regclass),
"repo_id" int8 NOT NULL,
"last_updated" timestamp(0) DEFAULT NULL::timestamp without time zone,
"issues_enabled" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"open_issues" int4,
"pull_requests_enabled" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"wiki_enabled" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"pages_enabled" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"fork_count" int4,
"default_branch" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"watchers_count" int4,
"UUID" int4,
"license" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"stars_count" int4,
"committers_count" int4,
"issue_contributors_count" varchar(255) COLLATE "default",
"changelog_file" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"contributing_file" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"license_file" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"code_of_conduct_file" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"security_issue_file" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"security_audit_file" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"status" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"keywords" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0),
CONSTRAINT "repo_info_pkey" PRIMARY KEY ("repo_info_id") 
)
WITHOUT OIDS;
ALTER TABLE "augur_data"."repo_info" OWNER TO "augur";

CREATE TABLE "augur_data"."repo_insights" (
"ri_id" int8 NOT NULL DEFAULT nextval('augur_data.repo_insights_ri_id_seq'::regclass),
"repo_id" int8,
"ri_metric" varchar COLLATE "default",
"ri_value" varchar(255) COLLATE "default",
"ri_date" timestamp(0),
"cms_id" int8,
"ri_fresh" bool,
"tool_source" varchar COLLATE "default",
"tool_version" varchar COLLATE "default",
"data_source" varchar COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "repo_insights_pkey" PRIMARY KEY ("ri_id") 
)
WITHOUT OIDS;
COMMENT ON TABLE "augur_data"."repo_insights" IS 'This table is output from an analytical worker inside of Augur. It runs through the different metrics on a repository and identifies the five to ten most “interesting” metrics as defined by some kind of delta or other factor. The algorithm is going to evolve. 

Worker Design Notes: The idea is that the "insight worker" will scan through a bunch of active metrics or "synthetic metrics" to list the most important insights. ';
COMMENT ON COLUMN "augur_data"."repo_insights"."ri_fresh" IS 'false if the date is before the statistic that triggered the insight, true if after. This allows us to automatically display only "fresh insights" and avoid displaying "stale insights". The insight worker will populate this table. ';
ALTER TABLE "augur_data"."repo_insights" OWNER TO "augur";

CREATE TABLE "augur_data"."repo_labor" (
"repo_labor_id" int8 NOT NULL DEFAULT nextval('augur_data.repo_labor_repo_labor_id_seq'::regclass),
"repo_id" int8,
"repo_clone_date" timestamp(0),
"rl_analysis_date" timestamp(0),
"programming_language" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"file_path" varchar(500) COLLATE "default" DEFAULT NULL::character varying,
"file_name" varchar(255) COLLATE "default" DEFAULT NULL::character varying,
"total_lines" int4,
"code_lines" int4,
"comment_lines" int4,
"blank_lines" int4,
"code_complexity" int4,
"repo_url" varchar(500) COLLATE "default" DEFAULT NULL::character varying,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0),
CONSTRAINT "repo_labor_pkey" PRIMARY KEY ("repo_labor_id") 
)
WITHOUT OIDS;
COMMENT ON TABLE "augur_data"."repo_labor" IS 'repo_labor is a derivative of tables used to store scc code and complexity counting statistics that are inputs to labor analysis, which are components of CHAOSS value metric calculations. ';
COMMENT ON COLUMN "augur_data"."repo_labor"."repo_url" IS 'This is a convenience column to simplify analysis against external datasets';
ALTER TABLE "augur_data"."repo_labor" OWNER TO "augur";

CREATE TABLE "augur_data"."repo_meta" (
"repo_id" int8 NOT NULL,
"rmeta_id" int8 NOT NULL DEFAULT nextval('augur_data.repo_meta_rmeta_id_seq'::regclass),
"rmeta_name" varchar(255) COLLATE "default",
"rmeta_value" varchar(255) COLLATE "default" DEFAULT 0,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0),
CONSTRAINT "repo_meta_pkey" PRIMARY KEY ("rmeta_id", "repo_id") 
)
WITHOUT OIDS;
COMMENT ON TABLE "augur_data"."repo_meta" IS 'Project Languages';
ALTER TABLE "augur_data"."repo_meta" OWNER TO "augur";

CREATE TABLE "augur_data"."repo_stats" (
"repo_id" int8 NOT NULL,
"rstat_id" int8 NOT NULL DEFAULT nextval('augur_data.repo_stats_rstat_id_seq'::regclass),
"rstat_name" varchar(400) COLLATE "default",
"rstat_value" int8,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0),
CONSTRAINT "repo_stats_pkey" PRIMARY KEY ("rstat_id", "repo_id") 
)
WITHOUT OIDS;
COMMENT ON TABLE "augur_data"."repo_stats" IS 'Project Watchers';
ALTER TABLE "augur_data"."repo_stats" OWNER TO "augur";

CREATE TABLE "augur_data"."repo_test_coverage" (
"repo_id" int8 NOT NULL DEFAULT nextval('augur_data.repo_test_coverage_repo_id_seq'::regclass),
"repo_clone_date" timestamp(0),
"rtc_analysis_date" timestamp(0),
"programming_language" varchar COLLATE "default",
"file_path" varchar COLLATE "default",
"file_name" varchar COLLATE "default",
"testing_tool" varchar COLLATE "default",
"file_statement_count" int8,
"file_subroutine_count" int8,
"file_statements_tested" int8,
"file_subroutines_tested" int8,
"tool_source" varchar COLLATE "default",
"tool_version" varchar COLLATE "default",
"data_source" varchar COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "repo_test_coverage_pkey" PRIMARY KEY ("repo_id") 
)
WITHOUT OIDS;
ALTER TABLE "augur_data"."repo_test_coverage" OWNER TO "augur";

CREATE TABLE "augur_data"."repos_fetch_log" (
"repos_id" int4 NOT NULL,
"status" varchar(128) COLLATE "default" NOT NULL,
"date" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP
)
WITHOUT OIDS;
CREATE INDEX "repos_id,status" ON "augur_data"."repos_fetch_log" USING btree ("repos_id" "pg_catalog"."int4_ops" ASC NULLS LAST, "status" "pg_catalog"."text_ops" ASC NULLS LAST);
ALTER TABLE "augur_data"."repos_fetch_log" OWNER TO "augur";

CREATE TABLE "augur_data"."settings" (
"id" int4 NOT NULL,
"setting" varchar(32) COLLATE "default" NOT NULL,
"value" varchar(128) COLLATE "default" NOT NULL,
"last_modified" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "settings_pkey" PRIMARY KEY ("id") 
)
WITHOUT OIDS;
ALTER TABLE "augur_data"."settings" OWNER TO "augur";

CREATE TABLE "augur_data"."unknown_cache" (
"type" varchar(10) COLLATE "default" NOT NULL,
"repo_group_id" int4 NOT NULL,
"email" varchar(128) COLLATE "default" NOT NULL,
"domain" varchar(128) COLLATE "default" DEFAULT 'NULL'::character varying,
"added" int8 NOT NULL,
"tool_source" varchar(255) COLLATE "default",
"tool_version" varchar(255) COLLATE "default",
"data_source" varchar(255) COLLATE "default",
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP
)
WITHOUT OIDS;
CREATE INDEX "type,projects_id" ON "augur_data"."unknown_cache" USING btree ("type" "pg_catalog"."text_ops" ASC NULLS LAST, "repo_group_id" "pg_catalog"."int4_ops" ASC NULLS LAST);
ALTER TABLE "augur_data"."unknown_cache" OWNER TO "augur";

CREATE TABLE "augur_data"."utility_log" (
"id" int8 NOT NULL DEFAULT nextval('augur_data.utility_log_id_seq1'::regclass),
"level" varchar(8) COLLATE "default" NOT NULL,
"status" varchar(128) COLLATE "default" NOT NULL,
"attempted" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "utility_log_pkey" PRIMARY KEY ("id") 
)
WITHOUT OIDS;
ALTER TABLE "augur_data"."utility_log" OWNER TO "augur";

CREATE TABLE "augur_data"."working_commits" (
"repos_id" int4 NOT NULL,
"working_commit" varchar(40) COLLATE "default" DEFAULT 'NULL'::character varying
)
WITHOUT OIDS;
ALTER TABLE "augur_data"."working_commits" OWNER TO "augur";

CREATE TABLE "augur_operations"."gh_worker_history" (
"history_id" int8 NOT NULL DEFAULT nextval('augur_operations.gh_worker_history_history_id_seq'::regclass),
"repo_id" int8,
"worker" varchar(255) COLLATE "default" NOT NULL,
"job_model" varchar(255) COLLATE "default" NOT NULL,
"oauth_id" int4 NOT NULL,
"timestamp" timestamp(0) NOT NULL,
"status" varchar(7) COLLATE "default" NOT NULL,
"total_results" int4,
CONSTRAINT "history_pkey" PRIMARY KEY ("history_id") 
)
WITHOUT OIDS;
ALTER TABLE "augur_operations"."gh_worker_history" OWNER TO "augur";

CREATE TABLE "augur_operations"."gh_worker_job" (
"job_model" varchar(255) COLLATE "default" NOT NULL,
"state" int4 NOT NULL DEFAULT 0,
"zombie_head" int4,
"since_id_str" varchar(255) COLLATE "default" NOT NULL DEFAULT '0'::character varying,
"description" varchar(255) COLLATE "default" DEFAULT 'I am a lazy piece of shit and I did not enter a description'::character varying,
"last_count" int4,
"last_run" timestamp(0) DEFAULT NULL::timestamp without time zone,
"analysis_state" int4 DEFAULT 0,
"oauth_id" int4 NOT NULL,
CONSTRAINT "job_pkey" PRIMARY KEY ("job_model") 
)
WITHOUT OIDS;
ALTER TABLE "augur_operations"."gh_worker_job" OWNER TO "augur";

CREATE TABLE "augur_operations"."gh_worker_oauth" (
"oauth_id" int4 NOT NULL,
"name" varchar(255) COLLATE "default" NOT NULL,
"consumer_key" varchar(255) COLLATE "default" NOT NULL,
"consumer_secret" varchar(255) COLLATE "default" NOT NULL,
"access_token" varchar(255) COLLATE "default" NOT NULL,
"access_token_secret" varchar(255) COLLATE "default" NOT NULL
)
WITHOUT OIDS;
ALTER TABLE "augur_operations"."gh_worker_oauth" OWNER TO "augur";

CREATE TABLE "spdx"."annotation_types" (
"annotation_type_id" int4 NOT NULL DEFAULT nextval('spdx.annotation_types_annotation_type_id_seq'::regclass),
"name" varchar(255) COLLATE "default" NOT NULL,
CONSTRAINT "annotation_types_pkey" PRIMARY KEY ("annotation_type_id") ,
CONSTRAINT "uc_annotation_type_name" UNIQUE ("name")
)
WITHOUT OIDS;
ALTER TABLE "spdx"."annotation_types" OWNER TO "augur";

CREATE TABLE "spdx"."annotations" (
"annotation_id" int4 NOT NULL DEFAULT nextval('spdx.annotations_annotation_id_seq'::regclass),
"document_id" int4 NOT NULL,
"annotation_type_id" int4 NOT NULL,
"identifier_id" int4 NOT NULL,
"creator_id" int4 NOT NULL,
"created_ts" timestamptz(6),
"comment" text COLLATE "default" NOT NULL,
CONSTRAINT "annotations_pkey" PRIMARY KEY ("annotation_id") 
)
WITHOUT OIDS;
ALTER TABLE "spdx"."annotations" OWNER TO "augur";

CREATE TABLE "spdx"."augur_repo_map" (
"repo_id" int8 NOT NULL,
"dosocs_id" varchar COLLATE "default",
"repo_path" varbit,
CONSTRAINT "augur_repo_map_pkey" PRIMARY KEY ("repo_id") 
)
WITHOUT OIDS;
ALTER TABLE "spdx"."augur_repo_map" OWNER TO "augur";

CREATE TABLE "spdx"."creator_types" (
"creator_type_id" int4 NOT NULL DEFAULT nextval('spdx.creator_types_creator_type_id_seq'::regclass),
"name" varchar(255) COLLATE "default" NOT NULL,
CONSTRAINT "creator_types_pkey" PRIMARY KEY ("creator_type_id") 
)
WITHOUT OIDS;
ALTER TABLE "spdx"."creator_types" OWNER TO "augur";

CREATE TABLE "spdx"."creators" (
"creator_id" int4 NOT NULL DEFAULT nextval('spdx.creators_creator_id_seq'::regclass),
"creator_type_id" int4 NOT NULL,
"name" varchar(255) COLLATE "default" NOT NULL,
"email" varchar(255) COLLATE "default" NOT NULL,
CONSTRAINT "creators_pkey" PRIMARY KEY ("creator_id") 
)
WITHOUT OIDS;
ALTER TABLE "spdx"."creators" OWNER TO "augur";

CREATE TABLE "spdx"."document_namespaces" (
"document_namespace_id" int4 NOT NULL DEFAULT nextval('spdx.document_namespaces_document_namespace_id_seq'::regclass),
"uri" varchar(500) COLLATE "default" NOT NULL,
CONSTRAINT "document_namespaces_pkey" PRIMARY KEY ("document_namespace_id") ,
CONSTRAINT "uc_document_namespace_uri" UNIQUE ("uri")
)
WITHOUT OIDS;
ALTER TABLE "spdx"."document_namespaces" OWNER TO "augur";

CREATE TABLE "spdx"."documents" (
"document_id" int4 NOT NULL DEFAULT nextval('spdx.documents_document_id_seq'::regclass),
"document_namespace_id" int4 NOT NULL,
"data_license_id" int4 NOT NULL,
"spdx_version" varchar(255) COLLATE "default" NOT NULL,
"name" varchar(255) COLLATE "default" NOT NULL,
"license_list_version" varchar(255) COLLATE "default" NOT NULL,
"created_ts" timestamptz(6) NOT NULL,
"creator_comment" text COLLATE "default" NOT NULL,
"document_comment" text COLLATE "default" NOT NULL,
"package_id" int4 NOT NULL,
CONSTRAINT "documents_pkey" PRIMARY KEY ("document_id") ,
CONSTRAINT "uc_document_document_namespace_id" UNIQUE ("document_namespace_id")
)
WITHOUT OIDS;
ALTER TABLE "spdx"."documents" OWNER TO "augur";

CREATE TABLE "spdx"."documents_creators" (
"document_creator_id" int4 NOT NULL DEFAULT nextval('spdx.documents_creators_document_creator_id_seq'::regclass),
"document_id" int4 NOT NULL,
"creator_id" int4 NOT NULL,
CONSTRAINT "documents_creators_pkey" PRIMARY KEY ("document_creator_id") 
)
WITHOUT OIDS;
ALTER TABLE "spdx"."documents_creators" OWNER TO "augur";

CREATE TABLE "spdx"."external_refs" (
"external_ref_id" int4 NOT NULL DEFAULT nextval('spdx.external_refs_external_ref_id_seq'::regclass),
"document_id" int4 NOT NULL,
"document_namespace_id" int4 NOT NULL,
"id_string" varchar(255) COLLATE "default" NOT NULL,
"sha256" varchar(64) COLLATE "default" NOT NULL,
CONSTRAINT "external_refs_pkey" PRIMARY KEY ("external_ref_id") ,
CONSTRAINT "uc_external_ref_document_id_string" UNIQUE ("document_id", "id_string")
)
WITHOUT OIDS;
ALTER TABLE "spdx"."external_refs" OWNER TO "augur";

CREATE TABLE "spdx"."file_contributors" (
"file_contributor_id" int4 NOT NULL DEFAULT nextval('spdx.file_contributors_file_contributor_id_seq'::regclass),
"file_id" int4 NOT NULL,
"contributor" text COLLATE "default" NOT NULL,
CONSTRAINT "file_contributors_pkey" PRIMARY KEY ("file_contributor_id") 
)
WITHOUT OIDS;
ALTER TABLE "spdx"."file_contributors" OWNER TO "augur";

CREATE TABLE "spdx"."file_types" (
"file_type_id" int4 NOT NULL DEFAULT nextval('spdx.file_types_file_type_id_seq'::regclass),
"name" varchar(255) COLLATE "default" NOT NULL,
CONSTRAINT "file_types_pkey" PRIMARY KEY ("file_type_id") ,
CONSTRAINT "uc_file_type_name" UNIQUE ("name")
)
WITHOUT OIDS;
ALTER TABLE "spdx"."file_types" OWNER TO "augur";

CREATE TABLE "spdx"."files" (
"file_id" int4 NOT NULL DEFAULT nextval('spdx.files_file_id_seq'::regclass),
"file_type_id" int4 NOT NULL,
"sha256" varchar(64) COLLATE "default" NOT NULL,
"copyright_text" text COLLATE "default",
"project_id" int4,
"comment" text COLLATE "default" NOT NULL,
"notice" text COLLATE "default" NOT NULL,
CONSTRAINT "files_pkey" PRIMARY KEY ("file_id") ,
CONSTRAINT "uc_file_sha256" UNIQUE ("sha256")
)
WITHOUT OIDS;
ALTER TABLE "spdx"."files" OWNER TO "augur";

CREATE TABLE "spdx"."files_licenses" (
"file_license_id" int4 NOT NULL DEFAULT nextval('spdx.files_licenses_file_license_id_seq'::regclass),
"file_id" int4 NOT NULL,
"license_id" int4 NOT NULL,
"extracted_text" text COLLATE "default" NOT NULL,
CONSTRAINT "files_licenses_pkey" PRIMARY KEY ("file_license_id") ,
CONSTRAINT "uc_file_license" UNIQUE ("file_id", "license_id")
)
WITHOUT OIDS;
ALTER TABLE "spdx"."files_licenses" OWNER TO "augur";

CREATE TABLE "spdx"."files_scans" (
"file_scan_id" int4 NOT NULL DEFAULT nextval('spdx.files_scans_file_scan_id_seq'::regclass),
"file_id" int4 NOT NULL,
"scanner_id" int4 NOT NULL,
CONSTRAINT "files_scans_pkey" PRIMARY KEY ("file_scan_id") ,
CONSTRAINT "uc_file_scanner_id" UNIQUE ("file_id", "scanner_id")
)
WITHOUT OIDS;
ALTER TABLE "spdx"."files_scans" OWNER TO "augur";

CREATE TABLE "spdx"."identifiers" (
"identifier_id" int4 NOT NULL DEFAULT nextval('spdx.identifiers_identifier_id_seq'::regclass),
"document_namespace_id" int4 NOT NULL,
"id_string" varchar(255) COLLATE "default" NOT NULL,
"document_id" int4,
"package_id" int4,
"package_file_id" int4,
CONSTRAINT "identifiers_pkey" PRIMARY KEY ("identifier_id") ,
CONSTRAINT "uc_identifier_document_namespace_id" UNIQUE ("document_namespace_id", "id_string"),
CONSTRAINT "uc_identifier_namespace_document_id" UNIQUE ("document_namespace_id", "document_id"),
CONSTRAINT "uc_identifier_namespace_package_id" UNIQUE ("document_namespace_id", "package_id"),
CONSTRAINT "uc_identifier_namespace_package_file_id" UNIQUE ("document_namespace_id", "package_file_id"),
CONSTRAINT "ck_identifier_exactly_one" CHECK ((((((document_id IS NOT NULL))::integer + ((package_id IS NOT NULL))::integer) + ((package_file_id IS NOT NULL))::integer) = 1))
)
WITHOUT OIDS;
ALTER TABLE "spdx"."identifiers" OWNER TO "augur";

CREATE TABLE "spdx"."licenses" (
"license_id" int4 NOT NULL DEFAULT nextval('spdx.licenses_license_id_seq'::regclass),
"name" varchar(255) COLLATE "default",
"short_name" varchar(255) COLLATE "default" NOT NULL,
"cross_reference" text COLLATE "default" NOT NULL,
"comment" text COLLATE "default" NOT NULL,
"is_spdx_official" bool NOT NULL,
CONSTRAINT "licenses_pkey" PRIMARY KEY ("license_id") ,
CONSTRAINT "uc_license_short_name" UNIQUE ("short_name")
)
WITHOUT OIDS;
ALTER TABLE "spdx"."licenses" OWNER TO "augur";

CREATE TABLE "spdx"."packages" (
"package_id" int4 NOT NULL DEFAULT nextval('spdx.packages_package_id_seq'::regclass),
"name" varchar(255) COLLATE "default" NOT NULL,
"version" varchar(255) COLLATE "default" NOT NULL,
"file_name" text COLLATE "default" NOT NULL,
"supplier_id" int4,
"originator_id" int4,
"download_location" text COLLATE "default",
"verification_code" varchar(64) COLLATE "default" NOT NULL,
"ver_code_excluded_file_id" int4,
"sha256" varchar(64) COLLATE "default",
"home_page" text COLLATE "default",
"source_info" text COLLATE "default" NOT NULL,
"concluded_license_id" int4,
"declared_license_id" int4,
"license_comment" text COLLATE "default" NOT NULL,
"copyright_text" text COLLATE "default",
"summary" text COLLATE "default" NOT NULL,
"description" text COLLATE "default" NOT NULL,
"comment" text COLLATE "default" NOT NULL,
"dosocs2_dir_code" varchar(64) COLLATE "default",
CONSTRAINT "packages_pkey" PRIMARY KEY ("package_id") ,
CONSTRAINT "uc_package_sha256" UNIQUE ("sha256"),
CONSTRAINT "uc_dir_code_ver_code" UNIQUE ("verification_code", "dosocs2_dir_code"),
CONSTRAINT "uc_sha256_ds2_dir_code_exactly_one" CHECK (((((sha256 IS NOT NULL))::integer + ((dosocs2_dir_code IS NOT NULL))::integer) = 1))
)
WITHOUT OIDS;
ALTER TABLE "spdx"."packages" OWNER TO "augur";

CREATE TABLE "spdx"."packages_files" (
"package_file_id" int4 NOT NULL DEFAULT nextval('spdx.packages_files_package_file_id_seq'::regclass),
"package_id" int4 NOT NULL,
"file_id" int4 NOT NULL,
"concluded_license_id" int4,
"license_comment" text COLLATE "default" NOT NULL,
"file_name" text COLLATE "default" NOT NULL,
CONSTRAINT "packages_files_pkey" PRIMARY KEY ("package_file_id") ,
CONSTRAINT "uc_package_id_file_name" UNIQUE ("package_id", "file_name")
)
WITHOUT OIDS;
ALTER TABLE "spdx"."packages_files" OWNER TO "augur";

CREATE TABLE "spdx"."packages_scans" (
"package_scan_id" int4 NOT NULL DEFAULT nextval('spdx.packages_scans_package_scan_id_seq'::regclass),
"package_id" int4 NOT NULL,
"scanner_id" int4 NOT NULL,
CONSTRAINT "packages_scans_pkey" PRIMARY KEY ("package_scan_id") ,
CONSTRAINT "uc_package_scanner_id" UNIQUE ("package_id", "scanner_id")
)
WITHOUT OIDS;
ALTER TABLE "spdx"."packages_scans" OWNER TO "augur";

CREATE TABLE "spdx"."projects" (
"project_id" int4 NOT NULL DEFAULT nextval('spdx.projects_project_id_seq'::regclass),
"name" text COLLATE "default" NOT NULL,
"homepage" text COLLATE "default" NOT NULL,
"uri" text COLLATE "default" NOT NULL,
CONSTRAINT "projects_pkey" PRIMARY KEY ("project_id") 
)
WITHOUT OIDS;
ALTER TABLE "spdx"."projects" OWNER TO "augur";

CREATE TABLE "spdx"."relationship_types" (
"relationship_type_id" int4 NOT NULL DEFAULT nextval('spdx.relationship_types_relationship_type_id_seq'::regclass),
"name" varchar(255) COLLATE "default" NOT NULL,
CONSTRAINT "relationship_types_pkey" PRIMARY KEY ("relationship_type_id") ,
CONSTRAINT "uc_relationship_type_name" UNIQUE ("name")
)
WITHOUT OIDS;
ALTER TABLE "spdx"."relationship_types" OWNER TO "augur";

CREATE TABLE "spdx"."relationships" (
"relationship_id" int4 NOT NULL DEFAULT nextval('spdx.relationships_relationship_id_seq'::regclass),
"left_identifier_id" int4 NOT NULL,
"right_identifier_id" int4 NOT NULL,
"relationship_type_id" int4 NOT NULL,
"relationship_comment" text COLLATE "default" NOT NULL,
CONSTRAINT "relationships_pkey" PRIMARY KEY ("relationship_id") ,
CONSTRAINT "uc_left_right_relationship_type" UNIQUE ("left_identifier_id", "right_identifier_id", "relationship_type_id")
)
WITHOUT OIDS;
ALTER TABLE "spdx"."relationships" OWNER TO "augur";

CREATE TABLE "spdx"."scanners" (
"scanner_id" int4 NOT NULL DEFAULT nextval('spdx.scanners_scanner_id_seq'::regclass),
"name" varchar(255) COLLATE "default" NOT NULL,
CONSTRAINT "scanners_pkey" PRIMARY KEY ("scanner_id") ,
CONSTRAINT "uc_scanner_name" UNIQUE ("name")
)
WITHOUT OIDS;
ALTER TABLE "spdx"."scanners" OWNER TO "augur";


ALTER TABLE "augur_data"."commit_comment_ref" ADD CONSTRAINT "fk_commit_comment_ref_commits_1" FOREIGN KEY ("cmt_id") REFERENCES "augur_data"."commits" ("cmt_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."commit_comment_ref" ADD CONSTRAINT "fk_commit_comment_ref_message_1" FOREIGN KEY ("msg_id") REFERENCES "augur_data"."message" ("msg_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."commit_parents" ADD CONSTRAINT "fk_commit_parents_commits_1" FOREIGN KEY ("cmt_id") REFERENCES "augur_data"."commits" ("cmt_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."commit_parents" ADD CONSTRAINT "fk_commit_parents_commits_2" FOREIGN KEY ("parent_id") REFERENCES "augur_data"."commits" ("cmt_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."commits" ADD CONSTRAINT "fk_commits_contributors_1" FOREIGN KEY ("cmt_ght_author_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."commits" ADD CONSTRAINT "fk_commits_contributors_2" FOREIGN KEY ("cmt_ght_committer_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."commits" ADD CONSTRAINT "fk_commits_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."contributor_affiliations" ADD CONSTRAINT "fk_contributor_affiliations_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."contributors_aliases" ADD CONSTRAINT "fk_contributors_aliases_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."contributors_history" ADD CONSTRAINT "fk_contributors_history_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."issue_assignees" ADD CONSTRAINT "fk_issue_assignees_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."issue_assignees" ADD CONSTRAINT "fk_issue_assignees_issues_1" FOREIGN KEY ("issue_id") REFERENCES "augur_data"."issues" ("issue_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."issue_events" ADD CONSTRAINT "fk_issue_events_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."issue_events" ADD CONSTRAINT "fk_issue_events_issues_1" FOREIGN KEY ("issue_id") REFERENCES "augur_data"."issues" ("issue_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."issue_labels" ADD CONSTRAINT "fk_issue_labels_issues_1" FOREIGN KEY ("issue_id") REFERENCES "augur_data"."issues" ("issue_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."issue_message_ref" ADD CONSTRAINT "fk_issue_message_ref_issues_1" FOREIGN KEY ("issue_id") REFERENCES "augur_data"."issues" ("issue_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."issue_message_ref" ADD CONSTRAINT "fk_issue_message_ref_message_1" FOREIGN KEY ("msg_id") REFERENCES "augur_data"."message" ("msg_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."issues" ADD CONSTRAINT "fk_issues_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."issues" ADD CONSTRAINT "fk_issues_contributors_2" FOREIGN KEY ("reporter_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."libraries" ADD CONSTRAINT "fk_libraries_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."library_dependencies" ADD CONSTRAINT "fk_library_dependencies_libraries_1" FOREIGN KEY ("library_id") REFERENCES "augur_data"."libraries" ("library_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."library_version" ADD CONSTRAINT "fk_library_version_libraries_1" FOREIGN KEY ("library_id") REFERENCES "augur_data"."libraries" ("library_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."message" ADD CONSTRAINT "fk_message_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."message" ADD CONSTRAINT "fk_message_platform_1" FOREIGN KEY ("pltfrm_id") REFERENCES "augur_data"."platform" ("pltfrm_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."message" ADD CONSTRAINT "fk_message_repo_groups_list_serve_1" FOREIGN KEY ("rgls_id") REFERENCES "augur_data"."repo_groups_list_serve" ("rgls_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."pull_request_assignees" ADD CONSTRAINT "fk_pull_request_assignees_contributors_1" FOREIGN KEY ("contrib_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."pull_request_assignees" ADD CONSTRAINT "fk_pull_request_assignees_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."pull_request_events" ADD CONSTRAINT "fk_pull_request_events_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."pull_request_events" ADD CONSTRAINT "fk_pull_request_events_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."pull_request_labels" ADD CONSTRAINT "fk_pull_request_labels_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."pull_request_message_ref" ADD CONSTRAINT "fk_pull_request_message_ref_message_1" FOREIGN KEY ("msg_id") REFERENCES "augur_data"."message" ("msg_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."pull_request_message_ref" ADD CONSTRAINT "fk_pull_request_message_ref_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."pull_request_meta" ADD CONSTRAINT "fk_pull_request_meta_contributors_2" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."pull_request_meta" ADD CONSTRAINT "fk_pull_request_meta_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."pull_request_repo" ADD CONSTRAINT "fk_pull_request_repo_contributors_1" FOREIGN KEY ("pr_cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."pull_request_repo" ADD CONSTRAINT "fk_pull_request_repo_pull_request_meta_1" FOREIGN KEY ("pr_repo_meta_id") REFERENCES "augur_data"."pull_request_meta" ("pr_repo_meta_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."pull_request_reviewers" ADD CONSTRAINT "fk_pull_request_reviewers_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."pull_request_reviewers" ADD CONSTRAINT "fk_pull_request_reviewers_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."pull_request_teams" ADD CONSTRAINT "fk_pull_request_teams_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."pull_requests" ADD CONSTRAINT "fk_pull_requests_pull_request_meta_1" FOREIGN KEY ("pr_meta_head_id") REFERENCES "augur_data"."pull_request_meta" ("pr_repo_meta_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."pull_requests" ADD CONSTRAINT "fk_pull_requests_pull_request_meta_2" FOREIGN KEY ("pr_meta_base_id") REFERENCES "augur_data"."pull_request_meta" ("pr_repo_meta_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."repo" ADD CONSTRAINT "fk_repo_repo_groups_1" FOREIGN KEY ("repo_group_id") REFERENCES "augur_data"."repo_groups" ("repo_group_id") ON UPDATE NO ACTION;
COMMENT ON CONSTRAINT "fk_repo_repo_groups_1" ON "augur_data"."repo" IS 'Repo_groups cardinality set to one and only one because, although in theory there could be more than one repo group for a repo, this might create dependecies in hosted situation that we do not want to live with. ';
ALTER TABLE "augur_data"."repo_badging" ADD CONSTRAINT "fk_repo_badging_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."repo_group_insights" ADD CONSTRAINT "fk_repo_group_insights_repo_groups_1" FOREIGN KEY ("repo_group_id") REFERENCES "augur_data"."repo_groups" ("repo_group_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."repo_groups_list_serve" ADD CONSTRAINT "fk_repo_groups_list_serve_repo_groups_1" FOREIGN KEY ("repo_group_id") REFERENCES "augur_data"."repo_groups" ("repo_group_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."repo_info" ADD CONSTRAINT "fk_repo_info_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."repo_labor" ADD CONSTRAINT "fk_repo_labor_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."repo_meta" ADD CONSTRAINT "fk_repo_meta_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."repo_stats" ADD CONSTRAINT "fk_repo_stats_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."repo_test_coverage" ADD CONSTRAINT "fk_repo_test_coverage_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."annotations" ADD CONSTRAINT "annotations_annotation_type_id_fkey" FOREIGN KEY ("annotation_type_id") REFERENCES "spdx"."annotation_types" ("annotation_type_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."annotations" ADD CONSTRAINT "annotations_creator_id_fkey" FOREIGN KEY ("creator_id") REFERENCES "spdx"."creators" ("creator_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."annotations" ADD CONSTRAINT "annotations_document_id_fkey" FOREIGN KEY ("document_id") REFERENCES "spdx"."documents" ("document_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."annotations" ADD CONSTRAINT "annotations_identifier_id_fkey" FOREIGN KEY ("identifier_id") REFERENCES "spdx"."identifiers" ("identifier_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."creators" ADD CONSTRAINT "creators_creator_type_id_fkey" FOREIGN KEY ("creator_type_id") REFERENCES "spdx"."creator_types" ("creator_type_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."documents" ADD CONSTRAINT "documents_data_license_id_fkey" FOREIGN KEY ("data_license_id") REFERENCES "spdx"."licenses" ("license_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."documents" ADD CONSTRAINT "documents_document_namespace_id_fkey" FOREIGN KEY ("document_namespace_id") REFERENCES "spdx"."document_namespaces" ("document_namespace_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."documents" ADD CONSTRAINT "documents_package_id_fkey" FOREIGN KEY ("package_id") REFERENCES "spdx"."packages" ("package_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."documents_creators" ADD CONSTRAINT "documents_creators_creator_id_fkey" FOREIGN KEY ("creator_id") REFERENCES "spdx"."creators" ("creator_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."documents_creators" ADD CONSTRAINT "documents_creators_document_id_fkey" FOREIGN KEY ("document_id") REFERENCES "spdx"."documents" ("document_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."external_refs" ADD CONSTRAINT "external_refs_document_id_fkey" FOREIGN KEY ("document_id") REFERENCES "spdx"."documents" ("document_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."external_refs" ADD CONSTRAINT "external_refs_document_namespace_id_fkey" FOREIGN KEY ("document_namespace_id") REFERENCES "spdx"."document_namespaces" ("document_namespace_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."file_contributors" ADD CONSTRAINT "file_contributors_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "spdx"."files" ("file_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."files" ADD CONSTRAINT "files_file_type_id_fkey" FOREIGN KEY ("file_type_id") REFERENCES "spdx"."file_types" ("file_type_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."files" ADD CONSTRAINT "files_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "spdx"."projects" ("project_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."files_licenses" ADD CONSTRAINT "files_licenses_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "spdx"."files" ("file_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."files_licenses" ADD CONSTRAINT "files_licenses_license_id_fkey" FOREIGN KEY ("license_id") REFERENCES "spdx"."licenses" ("license_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."files_scans" ADD CONSTRAINT "files_scans_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "spdx"."files" ("file_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."files_scans" ADD CONSTRAINT "files_scans_scanner_id_fkey" FOREIGN KEY ("scanner_id") REFERENCES "spdx"."scanners" ("scanner_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."identifiers" ADD CONSTRAINT "identifiers_document_id_fkey" FOREIGN KEY ("document_id") REFERENCES "spdx"."documents" ("document_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."identifiers" ADD CONSTRAINT "identifiers_document_namespace_id_fkey" FOREIGN KEY ("document_namespace_id") REFERENCES "spdx"."document_namespaces" ("document_namespace_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."identifiers" ADD CONSTRAINT "identifiers_package_file_id_fkey" FOREIGN KEY ("package_file_id") REFERENCES "spdx"."packages_files" ("package_file_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."identifiers" ADD CONSTRAINT "identifiers_package_id_fkey" FOREIGN KEY ("package_id") REFERENCES "spdx"."packages" ("package_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."packages" ADD CONSTRAINT "fk_package_packages_files" FOREIGN KEY ("ver_code_excluded_file_id") REFERENCES "spdx"."packages_files" ("package_file_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."packages" ADD CONSTRAINT "packages_concluded_license_id_fkey" FOREIGN KEY ("concluded_license_id") REFERENCES "spdx"."licenses" ("license_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."packages" ADD CONSTRAINT "packages_declared_license_id_fkey" FOREIGN KEY ("declared_license_id") REFERENCES "spdx"."licenses" ("license_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."packages" ADD CONSTRAINT "packages_originator_id_fkey" FOREIGN KEY ("originator_id") REFERENCES "spdx"."creators" ("creator_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."packages" ADD CONSTRAINT "packages_supplier_id_fkey" FOREIGN KEY ("supplier_id") REFERENCES "spdx"."creators" ("creator_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."packages_files" ADD CONSTRAINT "fk_package_files_packages" FOREIGN KEY ("package_id") REFERENCES "spdx"."packages" ("package_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."packages_files" ADD CONSTRAINT "packages_files_concluded_license_id_fkey" FOREIGN KEY ("concluded_license_id") REFERENCES "spdx"."licenses" ("license_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."packages_files" ADD CONSTRAINT "packages_files_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "spdx"."files" ("file_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."packages_scans" ADD CONSTRAINT "packages_scans_package_id_fkey" FOREIGN KEY ("package_id") REFERENCES "spdx"."packages" ("package_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."packages_scans" ADD CONSTRAINT "packages_scans_scanner_id_fkey" FOREIGN KEY ("scanner_id") REFERENCES "spdx"."scanners" ("scanner_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."relationships" ADD CONSTRAINT "relationships_left_identifier_id_fkey" FOREIGN KEY ("left_identifier_id") REFERENCES "spdx"."identifiers" ("identifier_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."relationships" ADD CONSTRAINT "relationships_relationship_type_id_fkey" FOREIGN KEY ("relationship_type_id") REFERENCES "spdx"."relationship_types" ("relationship_type_id") ON UPDATE NO ACTION;
ALTER TABLE "spdx"."relationships" ADD CONSTRAINT "relationships_right_identifier_id_fkey" FOREIGN KEY ("right_identifier_id") REFERENCES "spdx"."identifiers" ("identifier_id") ON UPDATE NO ACTION;
ALTER TABLE "augur_data"."repo_insights" ADD CONSTRAINT "fk_repo_insights_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id");

-- ----------------------------
-- Table structure for repos_import
-- ----------------------------
DROP TABLE IF EXISTS "augur_operations"."repos_import";
CREATE TABLE "augur_operations"."repos_import" (
  "repos_id" int8,
  "projects_id" int8,
  "repo_url" varchar COLLATE "pg_catalog"."default",
  "path" varchar COLLATE "pg_catalog"."default",
  "facade_name" varchar COLLATE "pg_catalog"."default",
  "added" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "status" varchar(255) COLLATE "pg_catalog"."default",
  "name" varchar COLLATE "pg_catalog"."default",
  "description" varchar COLLATE "pg_catalog"."default",
  "project_url" varchar COLLATE "pg_catalog"."default"
)
;
ALTER TABLE "augur_operations"."repos_import" OWNER TO "augur";
