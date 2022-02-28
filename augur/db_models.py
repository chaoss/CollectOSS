from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Import the flask app
# app = Flask(__name__)

# define the database connection string for Flask app
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

# TODO: Create db from Flask app
db = SQLAlchemy(app)


class Commits(db.Model):
    __tablename__ = 'commits'
    cmt_id = db.Column(db.Integer(length=64), primary_key=True, nullable=False)
    repo_id = db.Column(db.Integer(length=64), nullable=False)
    cmt_commit_hash = db.Column(db.VARCHAR(length=80), nullable=False)
    cmt_author_name = db.Column(db.String(), nullable=False)
    cmt_author_raw_email = db.Column(db.String(), nullable=False)
    cmt_author_email = db.Column(db.String(), nullable=False)
    cmt_author_date = db.Column(db.VARCHAR(length=10), nullable=False)
    cmt_author_affiliation = db.Column(db.String())
    cmt_committer_name = db.Column(db.String(), nullable=False)
    cmt_committer_raw_email = db.Column(db.String(), nullable=False)
    cmt_committer_email = db.Column(db.String(), nullable=False)
    cmt_committer_date = db.Column(db.String(), nullable=False)
    cmt_committer_affiliation = db.Column(db.String())
    cmt_added = db.Column(db.Integer(length=32), nullable=False)
    cmt_removed = db.Column(db.Integer(length=32), nullable=False)
    cmt_whitespace = db.Column(db.Integer(length=32), nullable=False)
    cmt_filename = db.Column(db.String(), nullable=False)
    cmt_date_attempted = db.Column(db.TIMESTAMP(), nullable=False)
    cmt_ght_author_id = db.Column(db.Integer(length=32))
    cmt_ght_committer_id = db.Column(db.Integer(length=32))
    cmt_ght_committed_at = db.Column(db.TIMESTAMP())
    cmt_committer_timestamp = db.Column(db.TIMESTAMP())
    cmt_author_timestamp = db.Column(db.TIMESTAMP())
    cmt_author_platform_username = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username
