# -*- coding: utf-8 -*-

import os
import json
import time
import logging
import tornado.web

from datetime import datetime, timedelta


class BaseHandler(tornado.web.RequestHandler):
    """
    Base handler gonna to be used instead of RequestHandler
    """

    def write_error(self, status_code, **kwargs):
        self.write("We've got some trouble(%s)" % status_code)

class ErrorHandler(tornado.web.ErrorHandler, BaseHandler):
    """
    Default handler gonna to be used in case of 404 error
    """
    pass