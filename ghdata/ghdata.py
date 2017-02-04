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

    def stargazers(self, repo=None, start=None, end=None):
        stargazers = self.__schema['watchers']
        q = s.select([stargazers])
        if (start or end):
            q = q.where(s.sql.text(self.__generate_predicate_dates(start, end)))
        if (repo):
            projects = self.__schema['projects']
            q = q.join(projects)
            q = q.where(projects.c.name == repo)
            return self.db.execute(str(q), name_1=repo)

