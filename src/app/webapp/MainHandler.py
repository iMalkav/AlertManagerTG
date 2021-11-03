# -*- coding: utf-8 -*-

import os
from os import path
import json
import time
import logging
import tornado.web

from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor  
from jinja2 import Environment, FileSystemLoader
from tornado.escape import json_encode
from datetime import datetime, timedelta
from dateutil.parser import parse

from app.webapp.BaseHandler import *
from app.webapp import route
from app.tgcli.cli_worker import cliWorker

from app.config.settings import _config

@route('/alerts', name = 'Receive alert from alertmanager')
class Alerts(BaseHandler):
    executor = ThreadPoolExecutor(max_workers = 4)

    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        messages = yield self.backgroud_task() 
        for phone, messages in messages.items():
            yield cliWorker.sendMsg(phone, '\n'.join(messages))
        return 200

    @run_on_executor
    def backgroud_task(self):
        messages = {}
        j2_env = Environment(loader=FileSystemLoader('templates'),
                         trim_blocks=True)
        alerts = json.loads(self.request.body)
        logging.debug(self.request.body)
        for alert in alerts['alerts']:
            phones = alert['labels']['phone'].split('|')
            if alert['status'] == 'resolved':
                startAt = parse(alert['startsAt'])
                endsAt = parse(alert['endsAt'])
                duration = endsAt - startAt
            else:
                duration = '00:00:00'
            msg = j2_env.get_template('template.html').render(
                                    message = alert, lasted = str(duration))
            for phone in phones:
                if phone not in messages:
                    messages[phone] = []
                messages[phone].append(msg)
        return messages

def make_app():
    settings = {
    'default_handler_class': ErrorHandler,
    'default_handler_args': dict(status_code=404),
    'debug': True,    
    }
    urls = route.urls
    application = tornado.web.Application(
    urls,
    **settings)
    return application
