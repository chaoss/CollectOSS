from werkzeug.routing import BaseConverter
import json

class ListConverter(BaseConverter):
    def to_python(self, value):
        return value.split('+')

    def to_url(self, values):
        return '+'.join(BaseConverter.to_url(value)
                        for value in values)

class BoolConverter(BaseConverter):
    def to_python(self, value):
        if value.lower() in ["false", "f", "n", "0"]:
            return False
        elif value.lower() in ["true", "t", "y", "1"]:
            return True

    def to_url(self, value):
        return str(value)

class JSONConverter(BaseConverter):
    def to_python(self, value):
        return json.loads(value)

    def to_url(self, value):
        return json.dumps(value)
