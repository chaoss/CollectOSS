import sqlalchemy as s
import records

class GHData:
    def __init__(self, dbstr):
        self.db = records.Database(dbstr)


    def __generate_predicate_dates(table, start=None, end=None):
        if (start and end):
            return "date(created_at) >= {} AND created_at <= {}".format(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
        elif (start): 
            return "date(created_at) >= {}".format(start.strftime('%Y-%m-%d'))
        elif (end):
            return "date(created_at) <= {}".format(end.strftime('%Y-%m-%d'))


    # Gets information about users
    def user(self, username=None, start=None, end=None):
        meta = s.MetaData()
        users = s.Table('users', meta, autoload=True, autoload_with=self.db.db)
        q = s.select([users])
        if (start or end):
            q = q.where(s.sql.text(self.__generate_predicate_dates(start, end)))
        if (username):
            q = q.where(s.sql.text('login IN (:username)').bindparams(s.bindparam('username')))
            return self.db.query(str(q), username=username)
        return self.db.query(str(q))