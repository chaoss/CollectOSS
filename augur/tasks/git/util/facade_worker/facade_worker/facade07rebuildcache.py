#!/usr/bin/env python3

# Copyright 2016-2018 Brian Warner
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier:  Apache-2.0

# Git repo maintenance
#
# This script is responsible for cloning new repos and keeping existing repos up
# to date. It can be run as often as you want (and will detect when it's
# already running, so as not to spawn parallel processes), but once or twice per
# day should be more than sufficient. Each time it runs, it updates the repo
# and checks for any parents of HEAD that aren't already accounted for in the
# repos. It also rebuilds analysis data, checks any changed affiliations and
# aliases, and caches data for display.
import sys
import platform
import imp
import time
import datetime
import html.parser
import subprocess
import os
import getopt
import xlsxwriter
import configparser
import sqlalchemy as s
from .facade02utilitymethods import update_repo_log, trim_commit, store_working_author, trim_author
# if platform.python_implementation() == 'PyPy':
#   import pymysql
# else:
#   import MySQLdb

def nuke_affiliations(session):

# Delete all stored affiliations in the database. Normally when you
# add/remove/change affiliation data via the web UI, any potentially affected
# records will be deleted and then rebuilt on the next run. However, if you
# manually add affiliation records via the database or import them by some other
# means, there's no elegant way to discover which affiliations are affected. So
# this is the scorched earth way: remove them all to force a total rebuild.
# Brutal but effective.

    session.log_activity('Info','Nuking affiliations')

    nuke = s.sql.text("""UPDATE commits SET cmt_author_affiliation = NULL,
            cmt_committer_affiliation = NULL""")

    session.execute_sql(nuke)

    session.log_activity('Info','Nuking affiliations (complete)')

def fill_empty_affiliations(session):

     

# When a record is added, it has no affiliation data. Also, when an affiliation
# mapping is changed via the UI, affiliation data will be set to NULL. This
# function finds any records with NULL affiliation data and fills them.

### Local helper functions ###
    def discover_null_affiliations(attribution,email):

    # Try a bunch of ways to match emails to attributions in the database. First it
    # tries to match exactly. If that doesn't work, it tries to match by domain. If
    # domain doesn't work, it strips subdomains from the email and tries again.

        # First we see if there's an exact match. This will also catch malformed or
        # intentionally mangled emails (e.g. "developer at domain.com") that have
        # been added as an affiliation rather than an alias.

        find_exact_match = s.sql.text("""SELECT ca_affiliation,ca_start_date
            FROM contributor_affiliations 
            WHERE ca_domain = :email 
            AND ca_active = 1 
            ORDER BY ca_start_date DESC""").bindparams(email=email)

         
         

        matches = session.fetchall_data_from_sql_text(find_exact_match)#list(cfg.cursor)

        if not matches and email.find('@') < 0:

            # It's not a properly formatted email, leave it NULL and log it.

            session.log_activity('Info',f"Unmatchable email: {email}")

            return

        if not matches:

            # Now we go for a domain-level match. Try for an exact match.

            domain = email[email.find('@')+1:]

            find_exact_domain = s.sql.text("""SELECT ca_affiliation,ca_start_date 
                FROM contributor_affiliations 
                WHERE ca_domain= :domain 
                AND ca_active = 1 
                ORDER BY ca_start_date DESC""").bindparams(domain=domain)

             
             

            matches = session.fetchall_data_from_sql_text(find_exact_domain)

        if not matches:

            # Then try stripping any subdomains.

            find_domain = s.sql.text("""SELECT ca_affiliation,ca_start_date 
                FROM contributor_affiliations 
                WHERE ca_domain = :strippedDomain 
                AND ca_active = 1 
                ORDER BY ca_start_date DESC""").bindparams(strippedDomain=domain[domain.rfind('.',0,domain.rfind('.',0))+1:])


            matches = session.fetchall_data_from_sql_text(find_domain)#list(cfg.cursor)

        if not matches:

            # One last check to see if it's an unmatched academic domain.

            if domain[-4:] in '.edu':
                matches.append({'ca_affiliation':'(Academic)','ca_start_date':'1970-01-01'})

        # Done looking. Now we process any matches that were found.

        if matches:

            session.log_activity('Debug',f"Found domain match for {email}")

            for match in matches:
                update = s.sql.text(("UPDATE commits "
                    f"SET cmt_{attribution}_affiliation = :affiliation "
                    f"WHERE cmt_{attribution}_email = :email "
                    f"AND cmt_{attribution}_affiliation IS NULL "
                    f"AND cmt_{attribution}_date::date >= {match['ca_start_date']}::date")
                    ).bindparams(affiliation=match['ca_affiliation'],email=email)

                session.log_activity('Info', f"attr: {attribution} \nmatch:{match}\nsql: {update}")

                try: 
                    session.execute_sql(update)
                except Exception as e: 
                    session.log_activity('Info', f"Error encountered: {e}")
                    session.log_activity('Info', f"Affiliation insertion failed for {email} ")

    def discover_alias(email):

    # Match aliases with their canonical email

        fetch_canonical = s.sql.text("""SELECT canonical_email
            FROM contributors_aliases
            WHERE alias_email=:email
            AND cntrb_active = 1""").bindparams(email=email)

        canonical = session.fetchall_data_from_sql_text(fetch_canonical)#list(cfg.cursor)

        if canonical:
            for email in canonical:
                return email['canonical_email']
        else:
            return email

### The real function starts here ###

    session.update_status('Filling empty affiliations')
    session.log_activity('Info','Filling empty affiliations')

    # Process any changes to the affiliations or aliases, and set any existing
    # entries in commits to NULL so they are filled properly.

    # First, get the time we started fetching since we'll need it later

    timefetch = s.sql.text("""SELECT current_timestamp(6) as fetched""")

    affiliations_fetched = session.execute_sql(timefetch).fetchone()[0] 
    print(affiliations_fetched)
    # Now find the last time we worked on affiliations, to figure out what's new

    affiliations_processed = session.get_setting('affiliations_processed')

    get_changed_affiliations = s.sql.text("""SELECT ca_domain FROM contributor_affiliations""")# WHERE "
        #"ca_last_used >= timestamptz  %s")

     

    changed_affiliations = session.fetchall_data_from_sql_text(get_changed_affiliations)#list(cfg.cursor)

    # Process any affiliations which changed since we last checked

    for changed_affiliation in changed_affiliations:

        session.log_activity('Debug',f"Resetting affiliation for {changed_affiliation['ca_domain']}")

        set_author_to_null = s.sql.text("""UPDATE commits SET cmt_author_affiliation = NULL
            WHERE cmt_author_email LIKE CONCAT('%%',:affiliation)""").bindparams(affiliation=changed_affiliation['ca_domain'])

        session.execute_sql(set_author_to_null)

        set_committer_to_null = s.sql.text("""UPDATE commits SET cmt_committer_affiliation = NULL
            WHERE cmt_committer_email LIKE CONCAT('%%',:affiliation)""").bindparams(affiliation=changed_affiliation['ca_domain'])

        session.execute_sql(set_committer_to_null)

    # Update the last fetched date, so we know where to start next time.

    update_affiliations_date = s.sql.text("""UPDATE settings SET value=:affiliations
        WHERE setting = 'affiliations_processed'""").bindparams(affiliations=affiliations_fetched)

    session.execute_sql(update_affiliations_date)

    # On to the aliases, now

    # First, get the time we started fetching since we'll need it later

    get_time = s.sql.text("""SELECT current_timestamp(6) as fetched""")

    aliases_fetched = session.execute_sql(get_time).fetchone()[0]#['fetched']

    # Now find the last time we worked on aliases, to figure out what's new

    aliases_processed = session.get_setting('aliases_processed')

    get_changed_aliases = s.sql.text("""SELECT alias_email FROM contributors_aliases WHERE
        cntrb_last_modified >= :aliases""").bindparams(aliases=aliases_processed)

    changed_aliases = session.fetchall_data_from_sql_text(get_changed_aliases)#list(cfg.cursor)

    # Process any aliases which changed since we last checked

    for changed_alias in changed_aliases:

        session.log_activity('Debug',f"Resetting affiliation for {changed_alias['alias_email']}")

        set_author_to_null = s.sql.text("""UPDATE commits SET cmt_author_affiliation = NULL
            WHERE cmt_author_raw_email LIKE CONCAT('%%',:alias)""").bindparams(alias=changed_alias['alias_email'])

        session.insert_or_update_data(set_author_to_null)

        set_committer_to_null = s.sql.text("""UPDATE commits SET cmt_committer_affiliation = NULL 
            WHERE cmt_committer_raw_email LIKE CONCAT('%%',:alias_email)""").bindparams(alias_email=changed_alias['alias_email'])

        session.insert_or_update_data(set_committer_to_null)

        reset_author = s.sql.text("""UPDATE commits
            SET cmt_author_email = :author_email 
            WHERE cmt_author_raw_email = :raw_author_email
            """).bindparams(author_email=discover_alias(changed_alias['alias_email']),raw_author_email=changed_alias['alias_email'])

        session.insert_or_update_data(reset_author)

        reset_committer = s.sql.text("""UPDATE commits
            SET cmt_committer_email = :author_email 
            WHERE cmt_committer_raw_email = :raw_author_email
            """).bindparams(author_email=discover_alias(changed_alias['alias_email']), raw_author_email=changed_alias['alias_email'])

        session.insert_or_update_data(reset_committer)
        
    # Update the last fetched date, so we know where to start next time.

    update_aliases_date = s.sql.text("""UPDATE settings SET value=:aliases
        WHERE setting = 'aliases_processed'""").bindparams(aliases=aliases_fetched)

    session.execute_sql(update_aliases_date)

    # Now rebuild the affiliation data

    working_author = session.get_setting('working_author')

    if working_author != 'done':
        session.log_activity('Error',f"Trimming author data in affiliations: {working_author}")
        trim_author(session, working_author)

    # Figure out which projects have NULL affiliations so they can be recached

    set_recache = s.sql.text("""UPDATE repo_groups 
                SET rg_recache=1  
                FROM repo_groups x, repo y, commits z 
                where x.repo_group_id = y.repo_group_id 
                and
                y."repo_id" = z.repo_id
                and 
        (z.cmt_author_affiliation IS NULL OR 
        z.cmt_committer_affiliation IS NULL)""")

    # ("UPDATE repo_groups p "
    #   "JOIN repo r ON p.repo_group_id = r.repo_group_id "
    #   "JOIN commits a ON r.repo_id = a.repo_id "
    #   "SET rg_recache=TRUE WHERE "
    #   "author_affiliation IS NULL OR "
    #   "committer_affiliation IS NULL")
    session.execute_sql(set_recache)

    # Find any authors with NULL affiliations and fill them

    find_null_authors = s.sql.text("""SELECT DISTINCT cmt_author_email AS email,
        MIN(cmt_author_date) AS earliest 
        FROM commits 
        WHERE cmt_author_affiliation IS NULL 
        GROUP BY cmt_author_email""")

    null_authors = session.fetchall_data_from_sql_text(find_null_authors)

    session.log_activity('Debug',f"Found {len(null_authors)} authors with NULL affiliation")

    for null_author in null_authors:

        email = null_author['email']

        store_working_author(session, email)

        discover_null_affiliations('author',email)

    store_working_author(session, 'done')

    # Find any committers with NULL affiliations and fill them

    find_null_committers = s.sql.text("""SELECT DISTINCT cmt_committer_email AS email, 
        MIN(cmt_committer_date) AS earliest 
        FROM commits 
        WHERE cmt_committer_affiliation IS NULL
        GROUP BY cmt_committer_email""")

    null_committers = session.fetchall_data_from_sql_text(find_null_committers)

    session.log_activity('Debug',f"Found {len(null_committers)} committers with NULL affiliation")

    for null_committer in null_committers:

        email = null_committer['email']

        store_working_author(session, email)

        discover_null_affiliations('committer',email)

    # Now that we've matched as much as possible, fill the rest as (Unknown)

    fill_unknown_author = s.sql.text("""UPDATE commits
        SET cmt_author_affiliation = '(Unknown)'
        WHERE cmt_author_affiliation IS NULL""")

    session.execute_sql(fill_unknown_author)

    fill_unknown_committer = s.sql.text("""UPDATE commits
        SET cmt_committer_affiliation = '(Unknown)'
        WHERE cmt_committer_affiliation IS NULL""")

    session.execute_sql(fill_unknown_committer)
    

    store_working_author(session, 'done')

    session.log_activity('Info','Filling empty affiliations (complete)')

def invalidate_caches(session):

# Invalidate all caches

    session.update_status('Invalidating caches')
    session.log_activity('Info','Invalidating caches')

    invalidate_cache = s.sql.text("""UPDATE repo_groups SET rg_recache = 1""")
    session.execute_sql(invalidate_cache)

    session.log_activity('Info','Invalidating caches (complete)')

def rebuild_unknown_affiliation_and_web_caches(session):

# When there's a lot of analysis data, calculating display data on the fly gets
# pretty expensive. Instead, we crunch the data based upon the user's preferred
# statistics (author or committer) and store them. We also store all records
# with an (Unknown) affiliation for display to the user.

    session.update_status('Caching data for display')
    session.log_activity('Info','Caching unknown affiliations and web data for display')

    report_date = session.get_setting('report_date')
    report_attribution = session.get_setting('report_attribution')

    # Clear stale caches

    clear_dm_repo_group_weekly = s.sql.text("""
            DELETE 
                FROM
                    dm_repo_group_weekly C USING repo_groups P 
                WHERE
                    P.repo_group_id = C.repo_group_id 
                    AND P.rg_recache = 1
        """)

    # ("DELETE c.* FROM dm_repo_group_weekly c "
    #   "JOIN repo_groups p ON c.repo_group_id = p.repo_group_id WHERE "
    #   "p.rg_recache=TRUE")
    session.execute_sql(clear_dm_repo_group_weekly)

    clear_dm_repo_group_monthly = s.sql.text("""
            DELETE 
                FROM
                    dm_repo_group_monthly C USING repo_groups P 
                WHERE
                    P.repo_group_id = C.repo_group_id 
                    AND P.rg_recache = 1
        """)

    # ("DELETE c.* FROM dm_repo_group_monthly c "
    #   "JOIN repo_groups p ON c.repo_group_id = p.repo_group_id WHERE "
    #   "p.rg_recache=TRUE")
    session.execute_sql(clear_dm_repo_group_monthly)

    clear_dm_repo_group_annual = s.sql.text("""
            DELETE 
                FROM
                    dm_repo_group_annual C USING repo_groups P 
                WHERE
                    P.repo_group_id = C.repo_group_id 
                    AND P.rg_recache = 1
        """)

    # ("DELETE c.* FROM dm_repo_group_annual c "
    #   "JOIN repo_groups p ON c.repo_group_id = p.repo_group_id WHERE "
    #   "p.rg_recache=TRUE")
    session.execute_sql(clear_dm_repo_group_annual)

    clear_dm_repo_weekly = s.sql.text("""
            DELETE 
                FROM
                    dm_repo_weekly C USING repo r,
                    repo_groups P 
                WHERE
                    C.repo_id = r.repo_id 
                    AND P.repo_group_id = r.repo_group_id 
                    AND P.rg_recache = 1
        """)

    # ("DELETE c.* FROM dm_repo_weekly c "
    #   "JOIN repo r ON c.repo_id = r.repo_id "
    #   "JOIN repo_groups p ON r.repo_group_id = p.repo_group_id WHERE "
    #   "p.rg_recache=TRUE")
    session.execute_sql(clear_dm_repo_weekly)

    clear_dm_repo_monthly = s.sql.text("""
            DELETE 
                FROM
                    dm_repo_monthly C USING repo r,
                    repo_groups P 
                WHERE
                    C.repo_id = r.repo_id 
                    AND P.repo_group_id = r.repo_group_id 
                    AND P.rg_recache = 1
        """)

    # ("DELETE c.* FROM dm_repo_monthly c "
    #   "JOIN repo r ON c.repo_id = r.repo_id "
    #   "JOIN repo_groups p ON r.repo_group_id = p.repo_group_id WHERE "
    #   "p.rg_recache=TRUE")
    session.execute_sql(clear_dm_repo_monthly)

    clear_dm_repo_annual = s.sql.text("""
            DELETE 
                FROM
                    dm_repo_annual C USING repo r,
                    repo_groups P 
                WHERE
                    C.repo_id = r.repo_id 
                    AND P.repo_group_id = r.repo_group_id 
                    AND P.rg_recache = 1
        """)

    # ("DELETE c.* FROM dm_repo_annual c "
    #   "JOIN repo r ON c.repo_id = r.repo_id "
    #   "JOIN repo_groups p ON r.repo_group_id = p.repo_group_id WHERE "
    #   "p.rg_recache=TRUE")
    session.execute_sql(clear_dm_repo_annual)

    clear_unknown_cache = s.sql.text("""
            DELETE 
                FROM
                    unknown_cache C USING repo_groups P 
                WHERE
                    P.repo_group_id = C.repo_group_id 
                    AND P.rg_recache = 1
        """)

    # ("DELETE c.* FROM unknown_cache c "
    #   "JOIN repo_groups p ON c.repo_group_id = p.repo_group_id WHERE "
    #   "p.rg_recache=TRUE")
    session.execute_sql(clear_unknown_cache)

    session.log_activity('Verbose','Caching unknown authors and committers')

    # Cache the unknown authors

    unknown_authors = s.sql.text("""
        INSERT INTO unknown_cache (type, repo_group_id, email, domain, added, tool_source, tool_version, data_source)
        SELECT 'author', 
        r.repo_group_id, 
        a.cmt_author_email, 
        SPLIT_PART(a.cmt_author_email,'@',2), 
        SUM(a.cmt_added),
        info.a AS tool_source, info.b AS tool_version, info.c AS data_source
        FROM (VALUES(:tool_source,:tool_version,:data_source)) info(a,b,c), 
        commits a 
        JOIN repo r ON r.repo_id = a.repo_id 
        JOIN repo_groups p ON p.repo_group_id = r.repo_group_id 
        WHERE a.cmt_author_affiliation = '(Unknown)' 
        AND p.rg_recache = 1 
        GROUP BY r.repo_group_id,a.cmt_author_email, info.a, info.b, info.c

        """).bindparams(tool_source=session.tool_source,tool_version=session.tool_version,data_source=session.data_source)

    session.execute_sql(unknown_authors)

    # Cache the unknown committers

    unknown_committers = s.sql.text("""INSERT INTO unknown_cache (type, repo_group_id, email, domain, added, tool_source, tool_version, data_source)
        SELECT 'committer', 
        r.repo_group_id, 
        a.cmt_committer_email, 
        SPLIT_PART(a.cmt_committer_email,'@',2), 
        SUM(a.cmt_added),
        info.a AS tool_source, info.b AS tool_version, info.c AS data_source
        FROM (VALUES(:tool_source,:tool_version,:data_source)) info(a,b,c), 
        commits a 
        JOIN repo r ON r.repo_id = a.repo_id 
        JOIN repo_groups p ON p.repo_group_id = r.repo_group_id 
        WHERE a.cmt_committer_affiliation = '(Unknown)' 
        AND p.rg_recache = 1 
        GROUP BY r.repo_group_id,a.cmt_committer_email, info.a, info.b, info.c 
        """).bindparams(tool_source=session.tool_source,tool_version=session.tool_version,data_source=session.data_source)

    session.execute_sql(unknown_committers)

    # Start caching by project

    session.log_activity('Verbose','Caching projects')

    cache_projects_by_week = s.sql.text((
        "INSERT INTO dm_repo_group_weekly (repo_group_id, email, affiliation, week, year, added, removed, whitespace, files, patches, tool_source, tool_version, data_source)"
        "SELECT r.repo_group_id AS repo_group_id," 
        f"a.cmt_{report_attribution}_email AS email, "
        f"a.cmt_{report_attribution}_affiliation AS affiliation," 
        f"date_part('week', TO_TIMESTAMP(a.cmt_{report_date}_date, 'YYYY-MM-DD')) AS week," 
        f"date_part('year', TO_TIMESTAMP(a.cmt_{report_date}_date, 'YYYY-MM-DD')) AS year, "
        "SUM(a.cmt_added) AS added, "
        "SUM(a.cmt_removed) AS removed," 
        "SUM(a.cmt_whitespace) AS whitespace, "
        "COUNT(DISTINCT a.cmt_filename) AS files," 
        "COUNT(DISTINCT a.cmt_commit_hash) AS patches,"
        "info.a AS tool_source, info.b AS tool_version, info.c AS data_source "
        "FROM (VALUES(:tool_source,:tool_version,:data_source)) info(a,b,c), "
        "commits a "
        "JOIN repo r ON r.repo_id = a.repo_id "
        "JOIN repo_groups p ON p.repo_group_id = r.repo_group_id "
        "LEFT JOIN exclude e ON "
        "    (a.cmt_author_email = e.email "
        "        AND (e.projects_id = r.repo_group_id "
        "            OR e.projects_id = 0)) "
        "    OR (a.cmt_author_email LIKE CONCAT('%%',e.domain) "
        "        AND (e.projects_id = r.repo_group_id "
        "        OR e.projects_id = 0)) "
        "WHERE e.email IS NULL " 
        "AND e.domain IS NULL " 
        "AND p.rg_recache = 1 "
        "GROUP BY week, "
        "year, "
        "affiliation, "
        f"a.cmt_{report_attribution}_email, "
        "r.repo_group_id, info.a, info.b, info.c")
        ).bindparams(tool_source=session.tool_source,tool_version=session.tool_version,data_source=session.data_source)

    session.execute_sql(cache_projects_by_week)

    cache_projects_by_month = s.sql.text(
        ("INSERT INTO dm_repo_group_monthly (repo_group_id, email, affiliation, month, year, added, removed, whitespace, files, patches, tool_source, tool_version, data_source) "
        "SELECT r.repo_group_id AS repo_group_id, "
        f"a.cmt_{report_attribution}_email AS email, "
        f"a.cmt_{report_attribution}_affiliation AS affiliation, "
        f"date_part('month', TO_TIMESTAMP(a.cmt_{report_date}_date, 'YYYY-MM-DD')) AS month, "
        f"date_part('year', TO_TIMESTAMP(a.cmt_{report_date}_date, 'YYYY-MM-DD')) AS year, "
        "SUM(a.cmt_added) AS added, "
        "SUM(a.cmt_removed) AS removed, "
        "SUM(a.cmt_whitespace) AS whitespace, "
        "COUNT(DISTINCT a.cmt_filename) AS files, "
        "COUNT(DISTINCT a.cmt_commit_hash) AS patches,"
        "info.a AS tool_source, info.b AS tool_version, info.c AS data_source "
        "FROM (VALUES(:tool_source,:tool_version,:data_source)) info(a,b,c), "
        "commits a "
        "JOIN repo r ON r.repo_id = a.repo_id "
        "JOIN repo_groups p ON p.repo_group_id = r.repo_group_id "
        "LEFT JOIN exclude e ON "
        "    (a.cmt_author_email = e.email "
        "        AND (e.projects_id = r.repo_group_id "
        "            OR e.projects_id = 0)) "
        "    OR (a.cmt_author_email LIKE CONCAT('%%',e.domain) "
        "        AND (e.projects_id = r.repo_group_id "
        "        OR e.projects_id = 0)) "
        "WHERE e.email IS NULL "
        "AND e.domain IS NULL "
        "AND p.rg_recache = 1 "
        "GROUP BY month, "
        "year, "
        "affiliation, "
        f"a.cmt_{report_attribution}_email,"
        "r.repo_group_id, info.a, info.b, info.c"
        )).bindparams(tool_source=session.tool_source,tool_version=session.tool_version,data_source=session.data_source)

    session.execute_sql(cache_projects_by_month)

    cache_projects_by_year = s.sql.text((
        "INSERT INTO dm_repo_group_annual (repo_group_id, email, affiliation, year, added, removed, whitespace, files, patches, tool_source, tool_version, data_source) "
        "SELECT r.repo_group_id AS repo_group_id, "
        f"a.cmt_{report_attribution}_email AS email, "
        f"a.cmt_{report_attribution}_affiliation AS affiliation, "
        f"date_part('year', TO_TIMESTAMP(a.cmt_{report_date}_date, 'YYYY-MM-DD')) AS year, "
        "SUM(a.cmt_added) AS added, "
        "SUM(a.cmt_removed) AS removed, "
        "SUM(a.cmt_whitespace) AS whitespace, "
        "COUNT(DISTINCT a.cmt_filename) AS files, "
        "COUNT(DISTINCT a.cmt_commit_hash) AS patches,"
        "info.a AS tool_source, info.b AS tool_version, info.c AS data_source "
        "FROM (VALUES(:tool_source,:tool_version,:data_source)) info(a,b,c), "
        "commits a "
        "JOIN repo r ON r.repo_id = a.repo_id "
        "JOIN repo_groups p ON p.repo_group_id = r.repo_group_id "
        "LEFT JOIN exclude e ON "
        "    (a.cmt_author_email = e.email "
        "        AND (e.projects_id = r.repo_group_id "
        "            OR e.projects_id = 0)) "
        "    OR (a.cmt_author_email LIKE CONCAT('%%',e.domain) "
        "        AND (e.projects_id = r.repo_group_id "
        "        OR e.projects_id = 0)) "
        "WHERE e.email IS NULL "
        "AND e.domain IS NULL "
        "AND p.rg_recache = 1 "
        "GROUP BY year, "
        "affiliation, "
        f"a.cmt_{report_attribution}_email,"
        "r.repo_group_id, info.a, info.b, info.c"

        
        
        )).bindparams(tool_source=session.tool_source,tool_version=session.tool_version,data_source=session.data_source)

     
     

    session.execute_sql(cache_projects_by_year)
    # Start caching by repo

    session.log_activity('Verbose','Caching repos')

    cache_repos_by_week = s.sql.text(
        (
        "INSERT INTO dm_repo_weekly (repo_id, email, affiliation, week, year, added, removed, whitespace, files, patches, tool_source, tool_version, data_source) "
        "SELECT a.repo_id AS repo_id, "
        f"a.cmt_{report_attribution}_email AS email, "
        f"a.cmt_{report_attribution}_affiliation AS affiliation, "
        f"date_part('week', TO_TIMESTAMP(a.cmt_{report_date}_date, 'YYYY-MM-DD')) AS week, "
        f"date_part('year', TO_TIMESTAMP(a.cmt_{report_date}_date, 'YYYY-MM-DD')) AS year, "
        "SUM(a.cmt_added) AS added, "
        "SUM(a.cmt_removed) AS removed, "
        "SUM(a.cmt_whitespace) AS whitespace, "
        "COUNT(DISTINCT a.cmt_filename) AS files, "
        "COUNT(DISTINCT a.cmt_commit_hash) AS patches,"
        "info.a AS tool_source, info.b AS tool_version, info.c AS data_source "
        "FROM (VALUES(:tool_source,:tool_version,:data_source)) info(a,b,c), "
        "commits a "
        "JOIN repo r ON r.repo_id = a.repo_id "
        "JOIN repo_groups p ON p.repo_group_id = r.repo_group_id "
        "LEFT JOIN exclude e ON "
        "    (a.cmt_author_email = e.email "
        "        AND (e.projects_id = r.repo_group_id "
        "            OR e.projects_id = 0)) "
        "    OR (a.cmt_author_email LIKE CONCAT('%%',e.domain) "
        "        AND (e.projects_id = r.repo_group_id "
        "        OR e.projects_id = 0)) "
        "WHERE e.email IS NULL "
        "AND e.domain IS NULL "
        "AND p.rg_recache = 1 "
        "GROUP BY week, "
        "year, "
        "affiliation, "
        f"a.cmt_{report_attribution}_email,"
        "a.repo_id, info.a, info.b, info.c"
        )).bindparams(tool_source=session.tool_source,tool_version=session.tool_version,data_source=session.data_source)

    session.execute_sql(cache_repos_by_week)

    cache_repos_by_month = s.sql.text((
        "INSERT INTO dm_repo_monthly (repo_id, email, affiliation, month, year, added, removed, whitespace, files, patches, tool_source, tool_version, data_source)"
        "SELECT a.repo_id AS repo_id, "
        f"a.cmt_{report_attribution}_email AS email, "
        f"a.cmt_{report_attribution}_affiliation AS affiliation, "
        f"date_part('month', TO_TIMESTAMP(a.cmt_{report_date}_date, 'YYYY-MM-DD')) AS month, "
        f"date_part('year', TO_TIMESTAMP(a.cmt_{report_date}_date, 'YYYY-MM-DD')) AS year, "
        "SUM(a.cmt_added) AS added, "
        "SUM(a.cmt_removed) AS removed, "
        "SUM(a.cmt_whitespace) AS whitespace, "
        "COUNT(DISTINCT a.cmt_filename) AS files, "
        "COUNT(DISTINCT a.cmt_commit_hash) AS patches, "
        "info.a AS tool_source, info.b AS tool_version, info.c AS data_source "
        "FROM (VALUES(:tool_source,:tool_version,:data_source)) info(a,b,c), "
        "commits a "
        "JOIN repo r ON r.repo_id = a.repo_id "
        "JOIN repo_groups p ON p.repo_group_id = r.repo_group_id "
        "LEFT JOIN exclude e ON "
        "    (a.cmt_author_email = e.email "
        "        AND (e.projects_id = r.repo_group_id "
        "            OR e.projects_id = 0)) "
        "    OR (a.cmt_author_email LIKE CONCAT('%%',e.domain) "
        "        AND (e.projects_id = r.repo_group_id "
        "        OR e.projects_id = 0)) "
        "WHERE e.email IS NULL "
        "AND e.domain IS NULL "
        "AND p.rg_recache = 1 "
        "GROUP BY month, "
        "year, "
        "affiliation, "
        f"a.cmt_{report_attribution}_email,"
        "a.repo_id, info.a, info.b, info.c"
        )).bindparams(tool_source=session.tool_source,tool_version=session.tool_version,data_source=session.data_source)

    session.execute_sql(cache_repos_by_month)

    cache_repos_by_year = s.sql.text((
        "INSERT INTO dm_repo_annual (repo_id, email, affiliation, year, added, removed, whitespace, files, patches, tool_source, tool_version, data_source)"
        "SELECT a.repo_id AS repo_id, "
        f"a.cmt_{report_attribution}_email AS email, "
        f"a.cmt_{report_attribution}_affiliation AS affiliation, "
        f"date_part('year', TO_TIMESTAMP(a.cmt_{report_date}_date, 'YYYY-MM-DD')) AS year, "
        "SUM(a.cmt_added) AS added, "
        "SUM(a.cmt_removed) AS removed, "
        "SUM(a.cmt_whitespace) AS whitespace, "
        "COUNT(DISTINCT a.cmt_filename) AS files, "
        "COUNT(DISTINCT a.cmt_commit_hash) AS patches, "
        "info.a AS tool_source, info.b AS tool_version, info.c AS data_source "
        "FROM (VALUES(:tool_source,:tool_version,:data_source)) info(a,b,c), "
        "commits a "
        "JOIN repo r ON r.repo_id = a.repo_id "
        "JOIN repo_groups p ON p.repo_group_id = r.repo_group_id "
        "LEFT JOIN exclude e ON "
        "    (a.cmt_author_email = e.email "
        "        AND (e.projects_id = r.repo_group_id "
        "            OR e.projects_id = 0)) "
        "    OR (a.cmt_author_email LIKE CONCAT('%%',e.domain) "
        "        AND (e.projects_id = r.repo_group_id "
        "        OR e.projects_id = 0)) "
        "WHERE e.email IS NULL "
        "AND e.domain IS NULL "
        "AND p.rg_recache = 1 "
        "GROUP BY year, "
        "affiliation, "
        f"a.cmt_{report_attribution}_email,"
        "a.repo_id, info.a, info.b, info.c"
        )).bindparams(tool_source=session.tool_source,tool_version=session.tool_version,data_source=session.data_source)

    session.execute_sql(cache_repos_by_year)

    # Reset cache flags

    reset_recache = s.sql.text("UPDATE repo_groups SET rg_recache = 0")
    session.execute_sql(reset_recache)

    session.log_activity('Info','Caching unknown affiliations and web data for display (complete)')

