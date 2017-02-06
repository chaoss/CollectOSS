#SPDX-License-Identifier: MIT

import sqlalchemy as s
import pandas as pd

class GHData(object):
    def __init__(self, dbstr):
        self.db = s.create_engine(dbstr)
        self.__schema = s.MetaData()
        self.__schema.reflect(bind=self.db)


    def __generate_predicate_dates(table, start=None, end=None):
        if (start and end):
            return "created_at >= '{}'' AND created_at <= '{}'".format(start.isoformat(), end.isoformat())
        elif (start): 
            return "created_at >= '{}'".format(start.isoformat())
        elif (end):
            return "created_at <= '{}'".format(end.isoformat())


    # Gets information about users
    def user(self, username=None, start=None, end=None):
        users = self.__schema.table['users']
        q = s.select([users])
        if (start or end):
            q = q.where(s.sql.text(self.__generate_predicate_dates(start, end)))
        if (username):
            q = q.where(users.c.login == username)
            return self.db.execute(str(q), login_1=username)
        return self.db.execute(str(q))

    def repoid(self, owner, repo):
        reposql = s.sql.text('SELECT projects.id FROM projects INNER JOIN users ON projects.owner_id = users.id WHERE projects.name = :repo AND users.login = :owner')
        result = self.db.execute(reposql, repo=repo, owner=owner,)
        repoid = 0
        for row in result:
            repoid = row[0]
        return repoid

    def stargazers(self, repoid, start=None, end=None):
        stargazersSQL = s.sql.text(
            """
            SELECT date(created_at) AS "date", COUNT(*) AS "watchers"
            FROM watchers
            WHERE repo_id = :repoid
            GROUP BY DATE(created_at)
            """)
        return pd.read_sql(stargazersSQL, self.db, params={"repoid": str(repoid)})

