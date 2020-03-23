from datetime import datetime
from dateutil.parser import parse


def flatten_json(json):
    '''

    Flattens a json response
    :param json: Dictionary: json object
    :return:
    '''
    out = {}

    def flatten(field, name=''):
        if type(field) is dict:
            for item in field:
                flatten(field[item], name + item + '_')
        elif type(field) is list:
            i = 0
            for item in field:
                flatten(str(item), name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = field

    flatten(json)
    return out


class RowDataSetter(object):
    """
    Class to help parse data extracted from JSON and convert into SQL compatible data types
    """
    def put_string(self, val):

        if isinstance(val, str):
            return val
        elif isinstance(val, unicode):
            return val.encode('utf-8')
        else:
            if isinstance(val, dict):
                val = str(val)
            if val:
                val = str(val)
            return val

    def put_int(self, val):

        if val is None:
            return val
        return int(val)

    def put_dt(self, val):

        if val is None:
            return val
        elif isinstance(val, str):
            val = datetime.strptime(val, '%Y-%m-%d')
        elif isinstance(val, unicode):
            temp = str(val).encode('utf-8')
            val = datetime.strptime(temp, '%Y-%m-%d')
        return val

    def put_dttm(self, val):

        if val is None:
            return val
        elif isinstance(val, unicode):
            temp = str(val).encode('utf-8')
            val = parse(temp)

        return val

    def put_float(self, val):

        if val is None:
            return val
        return float(val)

    def put_boolean(self, val):

        if val is None:
            return val
        return bool(val)

    def put_val(self, val):

        if isinstance(val, str):
            return val
        elif isinstance(val, unicode):
            return val.encode('utf-8')
        else:
            if isinstance(val, dict):
                val = str(val)
            return val
