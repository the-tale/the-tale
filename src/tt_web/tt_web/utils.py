
import time
import json
import datetime


def load_config(path):
    with open(path) as f:
        return json.load(f)


def postgres_time_to_timestamp(time_):
    return time.mktime(time_.timetuple()) + time_.microsecond / 1000000


def now(delta=0):
    return datetime.datetime.now() + datetime.timedelta(seconds=delta)
