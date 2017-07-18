
import json


def to_json(data, indent=None, debug=False):
    if debug:
        return json.dumps(data, ensure_ascii=False, check_circular=True, allow_nan=False, indent=2 if indent is None else indent)
    else:
        return json.dumps(data, ensure_ascii=False, check_circular=False, allow_nan=False, indent=indent)


def from_json(data):
    return json.loads(data)
