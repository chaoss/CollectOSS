# from augur.db.models.base import Base
# from sqlalchemy import (
#     Column,
#     Integer,
#     String,
#     UniqueConstraint,
#     PrimaryKeyConstraint,
#     ForeignKey,
#     Text,
#     Boolean,
#     TIMESTAMP,
#     JSON,
# )


# class AnnotationTypes(Base):
#     annotation_type_id = Column(Integer, primary_key=True)
#     name = Column(String(), nullable=False)

#     __tablename__ = "annotation_types"
#     __table_args__ = (
#         UniqueConstraint("name", name="uc_annotation_type_name"),
#         {"schema": "spdx"},
#     )


# class Annotations(Base):
#     annotation_id = Column(Integer, primary_key=True, nullable=False)
#     document_id = Column(
#         Integer,
#         ForeignKey("spdx.documents.document_id", name="annotations_document_id_fkey"),
#         nullable=False,
#     )
#     annotation_type_id = Column(
#         Integer,
#         ForeignKey(
#             "spdx.annotation_types.annotation_type_id",
#             name="annotations_annotation_type_id_fkey",
#         ),
#         nullable=False,
#     )
#     identifier_id = Column(
#         Integer,
#         ForeignKey(
#             "spdx.identifiers.identifier_id", name="annotations_identifier_id_fkey"
#         ),
#         nullable=False,
#     )
#     creator_id = Column(
#         Integer,
#         ForeignKey("spdx.creators.creator_id", name="annotations_creator_id_fkey"),
#         nullable=False,
#     )
#     created_ts = Column(TIMESTAMP(timezone=True))
#     comment = Column(Text(), nullable=False)

#     __tablename__ = "annotations"
#     __table_args__ = {"schema": "spdx"}


# class AugurRepoMap(Base):
#     map_id = Column(Integer, primary_key=True, nullable=False)
#     dosocs_pkg_id = Column(Integer)
#     dosocs_pkg_name = Column(Text())
#     repo_id = Column(Integer)
#     repo_path = Column(Text())

#     __tablename__ = "augur_repo_map"
#     __table_args__ = {"schema": "spdx"}


# class CreatorTypes(Base):
#     creator_type_id = Column(Integer, primary_key=True, nullable=False)
#     name = Column(String(), nullable=False)

#     __tablename__ = "creator_types"
#     __table_args__ = {"schema": "spdx"}


# class Creators(Base):
#     creator_id = Column(Integer, primary_key=True, nullable=False)
#     creator_type_id = Column(
#         Integer,
#         ForeignKey(
#             "spdx.creator_types.creator_type_id", name="creators_creator_type_id_fkey"
#         ),
#         nullable=False,
#     )
#     name = Column(String(), nullable=False)
#     email = Column(String(), nullable=False)

#     __tablename__ = "creators"
#     __table_args__ = {"schema": "spdx"}


# class DocumentNamespaces(Base):
#     document_namespace_id = Column(Integer, primary_key=True, nullable=False)
#     uri = Column(String(), nullable=False)

#     __tablename__ = "document_namespaces"
#     __table_args__ = (
#         UniqueConstraint("uri", name="uc_document_namespace_uri"),
#         {"schema": "spdx"},
#     )


# class Documents(Base):
#     document_id = Column(Integer, primary_key=True, nullable=False)
#     document_namespace_id = Column(
#         Integer,
#         ForeignKey(
#             "spdx.document_namespaces.document_namespace_id",
#             name="documents_document_namespace_id_fkey",
#         ),
#         nullable=False,
#     )
#     data_license_id = Column(
#         Integer,
#         ForeignKey("spdx.licenses.license_id", name="documents_data_license_id_fkey"),
#         nullable=False,
#     )
#     spdx_version = Column(String(), nullable=False)
#     name = Column(String(), nullable=False)
#     license_list_version = Column(String(), nullable=False)
#     created_ts = Column(TIMESTAMP(timezone=True), nullable=False)
#     creator_comment = Column(Text(), nullable=False)
#     document_comment = Column(Text(), nullable=False)
#     package_id = Column(
#         Integer,
#         ForeignKey("spdx.packages.package_id", name="documents_package_id_fkey"),
#         nullable=False,
#     )

#     __tablename__ = "documents"
#     __table_args__ = (
#         UniqueConstraint(
#             "document_namespace_id", name="uc_document_document_namespace_id"
#         ),
#         {"schema": "spdx"},
#     )


# class DocumentsCreators(Base):
#     document_creator_id = Column(Integer, primary_key=True, nullable=False)
#     document_id = Column(
#         Integer,
#         ForeignKey(
#             "spdx.documents.document_id", name="documents_creators_document_id_fkey"
#         ),
#         nullable=False,
#     )
#     creator_id = Column(
#         Integer,
#         ForeignKey(
#             "spdx.creators.creator_id", name="documents_creators_creator_id_fkey"
#         ),
#         nullable=False,
#     )

#     __tablename__ = "documents_creators"
#     __table_args__ = {"schema": "spdx"}


# class ExternalRefs(Base):
#     external_ref_id = Column(Integer, primary_key=True, nullable=False)
#     document_id = Column(
#         Integer,
#         ForeignKey("spdx.documents.document_id", name="external_refs_document_id_fkey"),
#         nullable=False,
#     )
#     document_namespace_id = Column(
#         Integer,
#         ForeignKey(
#             "spdx.document_namespaces.document_namespace_id",
#             name="external_refs_document_namespace_id_fkey",
#         ),
#         nullable=False,
#     )
#     id_string = Column(String(), nullable=False)
#     sha256 = Column(String(), nullable=False)

#     __tablename__ = "external_refs"
#     __table_args__ = (
#         UniqueConstraint(
#             "document_id", "id_string", name="uc_external_ref_document_id_string"
#         ),
#         {"schema": "spdx"},
#     )


# class FileContributors(Base):
#     file_contributor_id = Column(Integer, primary_key=True, nullable=False)
#     file_id = Column(
#         Integer,
#         ForeignKey("spdx.files.file_id", name="file_contributors_file_id_fkey"),
#         nullable=False,
#     )
#     contributor = Column(Text(), nullable=False)

#     __tablename__ = "file_contributors"
#     __table_args__ = {"schema": "spdx"}


# class FileTypes(Base):
#     file_type_id = Column(Integer)
#     name = Column(String(), nullable=False)

#     __tablename__ = "file_types"
#     __table_args__ = (
#         PrimaryKeyConstraint("name", name="uc_file_type_name"),
#         {"schema": "spdx"},
#     )


# class Files(Base):
#     file_id = Column(Integer, primary_key=True, nullable=False)
#     file_type_id = Column(Integer)
#     sha256 = Column(String(), nullable=False)
#     copyright_text = Column(Text())
#     package_id = Column(Integer)
#     comment = Column(Text(), nullable=False)
#     notice = Column(Text(), nullable=False)

#     __tablename__ = "files"
#     __table_args__ = (
#         UniqueConstraint("sha256", name="uc_file_sha256"),
#         {"schema": "spdx"},
#     )


# class FilesLicenses(Base):
#     file_license_id = Column(Integer, primary_key=True, nullable=False)
#     file_id = Column(
#         Integer,
#         ForeignKey("spdx.files.file_id", name="files_licenses_file_id_fkey"),
#         nullable=False,
#     )
#     license_id = Column(
#         Integer,
#         ForeignKey("spdx.licenses.license_id", name="files_licenses_license_id_fkey"),
#         nullable=False,
#     )
#     extracted_text = Column(Text(), nullable=False)

#     __tablename__ = "files_licenses"
#     __table_args__ = (
#         UniqueConstraint("file_id", "license_id", name="uc_file_license"),
#         {"schema": "spdx"},
#     )


# class FilesScans(Base):
#     file_scan_id = Column(Integer, primary_key=True, nullable=False)
#     file_id = Column(
#         Integer,
#         ForeignKey("spdx.files.file_id", name="files_scans_file_id_fkey"),
#         nullable=False,
#     )
#     scanner_id = Column(
#         Integer,
#         ForeignKey("spdx.scanners.scanner_id", name="files_scans_scanner_id_fkey"),
#         nullable=False,
#     )

#     __tablename__ = "files_scans"
#     __table_args__ = (
#         UniqueConstraint("file_id", "scanner_id", name="uc_file_scanner_id"),
#         {"schema": "spdx"},
#     )


# # TODO: Add check to table


# class Identifiers(Base):
#     identifier_id = Column(Integer, primary_key=True, nullable=False)
#     document_namespace_id = Column(
#         Integer,
#         ForeignKey(
#             "spdx.document_namespaces.document_namespace_id",
#             name="identifiers_document_namespace_id_fkey",
#         ),
#         nullable=False,
#     )
#     id_string = Column(String(), nullable=False)
#     document_id = Column(
#         Integer,
#         ForeignKey("spdx.documents.document_id", name="identifiers_document_id_fkey"),
#     )
#     package_id = Column(
#         Integer,
#         ForeignKey("spdx.packages.package_id", name="identifiers_package_id_fkey"),
#     )
#     package_file_id = Column(
#         Integer,
#         ForeignKey(
#             "spdx.packages_files.package_file_id",
#             name="identifiers_package_file_id_fkey",
#         ),
#     )

#     __tablename__ = "identifiers"
#     __table_args__ = (
#         UniqueConstraint(
#             "document_namespace_id",
#             "id_string",
#             name="uc_identifier_document_namespace_id",
#         ),
#         UniqueConstraint(
#             "document_namespace_id",
#             "document_id",
#             name="uc_identifier_namespace_document_id",
#         ),
#         UniqueConstraint(
#             "document_namespace_id",
#             "package_id",
#             name="uc_identifier_namespace_package_id",
#         ),
#         UniqueConstraint(
#             "document_namespace_id",
#             "package_file_id",
#             name="uc_identifier_namespace_package_file_id",
#         ),
#         {"schema": "spdx"},
#     )


# class Licenses(Base):
#     license_id = Column(Integer, primary_key=True)
#     name = Column(String())
#     short_name = Column(String(), nullable=False)
#     cross_reference = Column(Text(), nullable=False)
#     comment = Column(Text(), nullable=False)
#     is_spdx_official = Column(Boolean(), nullable=False)

#     __tablename__ = "licenses"
#     __table_args__ = (
#         UniqueConstraint("short_name", name="uc_license_short_name"),
#         {"schema": "spdx"},
#     )


# # TODO: Need to a check


# class Packages(Base):
#     package_id = Column(Integer, primary_key=True)
#     name = Column(String(), nullable=False)
#     version = Column(String(), nullable=False)
#     file_name = Column(Text(), nullable=False)
#     supplier_id = Column(
#         Integer,
#         ForeignKey("spdx.creators.creator_id", name="packages_supplier_id_fkey"),
#     )
#     originator_id = Column(
#         Integer,
#         ForeignKey("spdx.creators.creator_id", name="packages_originator_id_fkey"),
#     )
#     download_location = Column(Text())
#     verification_code = Column(String(), nullable=False)
#     ver_code_excluded_file_id = Column(
#         Integer,
#         ForeignKey(
#             "spdx.packages_files.package_file_id", name="fk_package_packages_files"
#         ),
#     )
#     sha256 = Column(String())
#     home_page = Column(Text())
#     source_info = Column(Text(), nullable=False)
#     concluded_license_id = Column(
#         Integer,
#         ForeignKey(
#             "spdx.licenses.license_id", name="packages_concluded_license_id_fkey"
#         ),
#     )
#     declared_license_id = Column(
#         Integer,
#         ForeignKey(
#             "spdx.licenses.license_id", name="packages_declared_license_id_fkey"
#         ),
#     )
#     license_comment = Column(Text(), nullable=False)
#     copyright_text = Column(Text())
#     summary = Column(Text(), nullable=False)
#     description = Column(Text(), nullable=False)
#     comment = Column(Text(), nullable=False)
#     dosocs2_dir_code = Column(String())

#     __tablename__ = "packages"
#     __table_args__ = (
#         UniqueConstraint("sha256", name="uc_package_sha256"),
#         UniqueConstraint(
#             "verification_code", "dosocs2_dir_code", name="uc_dir_code_ver_code"
#         ),
#         {"schema": "spdx"},
#     )


# class PackagesFiles(Base):
#     package_file_id = Column(Integer, primary_key=True)
#     package_id = Column(
#         Integer,
#         ForeignKey("spdx.packages.package_id", name="fk_package_files_packages"),
#         nullable=False,
#     )
#     file_id = Column(
#         Integer,
#         ForeignKey("spdx.files.file_id", name="packages_files_file_id_fkey"),
#         nullable=False,
#     )
#     concluded_license_id = Column(
#         Integer,
#         ForeignKey(
#             "spdx.licenses.license_id", name="packages_files_concluded_license_id_fkey"
#         ),
#     )
#     license_comment = Column(Text(), nullable=False)
#     file_name = Column(Text(), nullable=False)

#     __tablename__ = "packages_files"
#     __table_args__ = (
#         UniqueConstraint("package_id", "file_name", name="uc_package_id_file_name"),
#         {"schema": "spdx"},
#     )


# class PackagesScans(Base):
#     package_scan_id = Column(Integer, primary_key=True)
#     package_id = Column(
#         Integer,
#         ForeignKey("spdx.packages.package_id", name="packages_scans_package_id_fkey"),
#         nullable=False,
#     )
#     scanner_id = Column(
#         Integer,
#         ForeignKey("spdx.scanners.scanner_id", name="packages_scans_scanner_id_fkey"),
#         nullable=False,
#     )

#     __tablename__ = "packages_scans"
#     __table_args__ = (
#         UniqueConstraint("package_id", "scanner_id", name="uc_package_scanner_id"),
#         {"schema": "spdx"},
#     )


# class Projects(Base):
#     package_id = Column(Integer, primary_key=True)
#     name = Column(Text(), nullable=False)
#     homepage = Column(Text(), nullable=False)
#     uri = Column(Text(), nullable=False)

#     __tablename__ = "projects"
#     __table_args__ = {"schema": "spdx"}


# class RelationshipTypes(Base):
#     relationship_type_id = Column(Integer, primary_key=True)
#     name = Column(String(), nullable=False)

#     __tablename__ = "relationship_types"
#     __table_args__ = (
#         UniqueConstraint("name", name="uc_relationship_type_name"),
#         {"schema": "spdx"},
#     )


# class Relationships(Base):
#     relationship_id = Column(Integer, primary_key=True)
#     left_identifier_id = Column(
#         Integer,
#         ForeignKey(
#             "spdx.identifiers.identifier_id",
#             name="relationships_left_identifier_id_fkey",
#         ),
#         nullable=False,
#     )
#     right_identifier_id = Column(
#         Integer,
#         ForeignKey(
#             "spdx.identifiers.identifier_id",
#             name="relationships_right_identifier_id_fkey",
#         ),
#         nullable=False,
#     )
#     relationship_type_id = Column(
#         Integer,
#         ForeignKey(
#             "spdx.relationship_types.relationship_type_id",
#             name="relationships_relationship_type_id_fkey",
#         ),
#         nullable=False,
#     )
#     relationship_comment = Column(Text(), nullable=False)

#     __tablename__ = "relationships"
#     __table_args__ = (
#         UniqueConstraint(
#             "left_identifier_id",
#             "right_identifier_id",
#             "relationship_type_id",
#             name="uc_left_right_relationship_type",
#         ),
#         {"schema": "spdx"},
#     )


# class SbomScans(Base):
#     sbom_scan_id = Column(Integer, primary_key=True)
#     repo_id = Column(Integer)
#     sbom_scan = Column(JSON())

#     __tablename__ = "sbom_scans"
#     __table_args__ = {"schema": "spdx"}


# class Scanners(Base):
#     scanner_id = Column(Integer, primary_key=True)
#     name = Column(String(), nullable=False)

#     __tablename__ = "scanners"
#     __table_args__ = (
#         UniqueConstraint("name", name="uc_scanner_name"),
#         {"schema": "spdx"},
#     )
