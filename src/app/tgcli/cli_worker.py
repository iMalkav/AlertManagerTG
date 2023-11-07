# -*- coding: utf-8 -*-
import logging
import datetime
import time

from pyrogram import Client, filters, errors
from pyrogram.types import InputPhoneContact
from pyrogram.handlers import MessageHandler

from app.config.settings import _config
from app.lang import _lang

from app.tgcli.commands import _command
from app.tgcli.admin import *
from app.tgcli.monitoring import *
from app.tgcli.help import *
from app.tgcli.exeptions import NotFoundTGAccountException


class TGCli(object):

    def __init__(self, *args, **kwargs):
        self.cliapp = Client(_config.cliSession,
                             _config.cliApiId, _config.cliApiHash)
        self.cliapp.start()
        self.reg_handler()
        self.CONTACTS = []
        self.init_contacts()

    def reg_handler(self):
        self.cliapp.add_handler(MessageHandler(self.who_am_i, filters.command(
            _command.get_command_name('me'), _command.get_command_pref('me'))))
        self.cliapp.add_handler(MessageHandler(service_state, filters.command(
            _command.get_command_name('state'), _command.get_command_pref('state'))))
        self.cliapp.add_handler(MessageHandler(prometheus_state, filters.command(
            _command.get_command_name('prom'), _command.get_command_pref('prom'))))
        self.cliapp.add_handler(MessageHandler(alerts_state, filters.command(
            _command.get_command_name('alerts'), _command.get_command_pref('alerts'))))
        self.cliapp.add_handler(MessageHandler(metric_state, filters.command(
            _command.get_command_name('metric'), _command.get_command_pref('metric'))))
        self.cliapp.add_handler(MessageHandler(help, filters.command(
            _command.get_command_name('help'), _command.get_command_pref('help'))))
        self.cliapp.add_handler(MessageHandler(man, filters.command(
            _command.get_command_name('man'), _command.get_command_pref('man'))))

    def stop(self):
        self.cliapp.stop()

    def init_contacts(self):
        temp = self.cliapp.get_contacts()
        for contact in temp:
            if contact.phone_number != None and contact.phone_number not in self.CONTACTS:
                self.CONTACTS.append(contact)
        return self.CONTACTS

    def who_am_i(self, client, message):
        logging.info('Recieve command "me" message from user({0}) Phone:{1} Name: {3} {2} Username:{4}'.format(message.from_user.id, message.from_user.phone_number,
                                                                                                               message.from_user.last_name, message.from_user.first_name, message.from_user.username))
        client.send_message(message.from_user.id,
                            'Ваш ID: {}'.format(message.from_user.id))

    async def sendMsg(self, phone, msg):
        try:
            contact = await self.get_or_create_contact(phone)
            await self.cliapp.send_message(contact.id, msg)
        except errors.FloodWait as e:
            time.sleep(e.x)
            self.sendMsg(phone, msg)

    async def get_or_create_contact(self, phone):
        for contact in self.CONTACTS:
            if contact.phone_number in phone:
                return contact
        contact = await self.cliapp.import_contacts([InputPhoneContact(phone, phone),])
        if len(contact.users) > 0:
            self.CONTACTS.append(contact.users[0])
            return contact.users[0]
        else:
            raise NotFoundTGAccountException(
                "No found telegramm account. Phone {}".format(phone))


cliWorker = TGCli()
