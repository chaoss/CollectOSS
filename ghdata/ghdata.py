#SPDX-License-Identifier: MIT

import sqlalchemy as s
import records

class GHData:
    def __init__(self, dbstr):
        self.db = records.Database(dbstr)


    def __generate_predicate_dates(table, start=None, end=None):
        if (start and end):
            return "created_at >= '{}'' AND created_at <= '{}'".format(start.isoformat(), end.isoformat())
        elif (start): 
            return "created_at >= '{}'".format(start.isoformat())
        elif (end):
            return "created_at <= '{}'".format(end.isoformat())


    # Gets information about users
    def user(self, username=None, start=None, end=None):
        meta = s.MetaData()
        users = s.Table('users', meta, autoload=True, autoload_with=self.db.db)
        q = s.select([users])
        if (start or end):
            q = q.where(s.sql.text(self.__generate_predicate_dates(start, end)))
        if (username):
            q = q.where(users.c.login == username)
            return self.db.query(str(q), login_1=username)
        return self.db.query(str(q))