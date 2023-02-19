import json


class JSONFormatter:
    @staticmethod
    def format(json_object):
        return json.dumps(json_object, indent=2)
