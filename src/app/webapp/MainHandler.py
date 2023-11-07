# -*- coding: utf-8 -*-

import os
import sys
from os import path
import json
import time
import logging
import tornado.web
import asyncio
import multiprocessing


from multiprocessing import Pool
from functools import partial
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from jinja2 import Environment, FileSystemLoader
from tornado.escape import json_encode
from datetime import datetime, timedelta
from dateutil.parser import parse

from app.webapp.BaseHandler import *
from app.webapp import route
from app.tgcli.cli_worker import cliWorker
from app.tgcli.exeptions import NotFoundTGAccountException
from app.config.settings import _config


@route('/alerts', name='Receive alert from alertmanager')
class Alerts(BaseHandler):
    executor = ThreadPoolExecutor(max_workers=4)

    async def send_messages(self, phone, messages):
        """
        Asynchronously sends messages to a phone number.

        :param phone: A string representing the phone number to send the message to.
        :param messages: A list of strings representing the messages to send.
        :return: None.

        Sends the messages to the specified phone number using the `cliWorker.sendMsg` method. If the phone number is not found, the function silently skips it.
        """
        try:
            await cliWorker.sendMsg(phone, '\n'.join(messages))
        except NotFoundTGAccountException:
            pass  # Skip phone

    async def post(self, *args, **kwargs):
        """
        Asynchronously sends messages to multiple phones using multiprocessing.

        :param args: Variable length argument list.
        :param kwargs: Arbitrary keyword arguments.
        :return: An HTTP 200 response code.
        """
        messages = await self.background_task()
        tasks = []
        with multiprocessing.Pool() as pool:
            for phone, messages in messages.items():
                tasks.append(asyncio.ensure_future(
                    self.send_messages(phone, messages)))
            await asyncio.gather(*tasks)
        return 200

    # def process_alert(alert, j2_env, phones_to_messages):
    #    """
    #    Process an alert and send messages to associated phones.
#
    #    Args:
    #        alert (dict): A dictionary containing information about the alert.
    #        j2_env (jinja2.Environment): A Jinja2 environment object.
#
    #    Returns:
    #        None
    #    """
    #    phones = alert['labels']['phone'].split('|')
    #    if alert['status'] == 'resolved':
    #        start_at = parse(alert['startsAt'])
    #        ends_at = parse(alert['endsAt'])
    #        duration = ends_at - start_at
    #    else:
    #        duration = '00:00:00'
    #    msg = j2_env.get_template('template.html').render(
    #        message=alert, lasted=str(duration))
    #    for phone in phones:
    #        if phone not in phones_to_messages:
    #            phones_to_messages[phone] = []
    #        phones_to_messages[phone].append(msg)
#
    # @run_on_executor
    # def background_task(self):
    #    """
    #    Executes a background task that processes alerts and sends messages to phones.
    #    Uses a thread pool to process alerts in parallel and a Jinja2 template to render messages.
#
    #    Returns:
    #    A dictionary containing phone numbers as keys and a list of messages as values.
    #    """
    #    alerts = json.loads(self.request.body)
    #    logging.debug(self.request.body)
    #    phones_to_messages = {}
#
    #    with Pool() as pool:
    #        j2_env = Environment(loader=FileSystemLoader(
    #            'templates'), trim_blocks=True)
    #        partial_process_alert = partial(
    #            self.process_alert, j2_env=j2_env, phones_to_messages=phones_to_messages)
    #        pool.map(partial_process_alert, [
    #                     (alert, j2_env, phones_to_messages) for alert in alerts['alerts']])
#
    #    return phones_to_messages

    @run_on_executor
    def background_task(self):
        messages = {}
        main_script_path = sys.argv[0]
        main_script_dir = os.path.dirname(
            os.path.abspath(main_script_path))
        templates_dir = os.path.join(
            main_script_dir, 'templates')
        j2_env = Environment(loader=FileSystemLoader(templates_dir),
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
                message=alert, lasted=str(duration))
            for phone in phones:
                if phone not in messages:
                    messages[phone] = []
                messages[phone].append(msg)
        return messages


def make_app():
    """
    Creates a Tornado web application instance.

    Returns:
        tornado.web.Application: The web application instance.
    """
    error_handler_class = ErrorHandler
    error_handler_args = {'status_code': 404}
    debug = True

    settings = {
        'default_handler_class': error_handler_class,
        'default_handler_args': error_handler_args,
        'debug': debug,
    }

    urls = route.urls
    application = tornado.web.Application(urls, **settings)
    return application
