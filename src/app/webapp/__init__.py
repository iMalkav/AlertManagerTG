# -*- coding: utf-8 -*-
import os
import json
import time
import logging
import tornado.web

from datetime import datetime, timedelta

# route
class Route(object):
    urls = []

    def __call__(self, url, name=None):
        def _(cls):
            self.urls.append(tornado.web.URLSpec(url, cls, name=name))
            return cls
        return _


route = Route()


def _pyTimeToUnixTime(pytime):
    return int(time.mktime(pytime.timetuple()))

def jsonify(fn):
    def tmp(*args, **kw):
        try:
            ret = {"status": "ok",
                   "result": fn(*args, **kw)}
        except Exception as e:
            ret = {"status" : "err", "descr" : str(e)}
        return ret # json.dumps(ret)

    return tmp
