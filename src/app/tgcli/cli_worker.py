# -*- coding: utf-8 -*-
import logging
import datetime
import time

from pyrogram import Client, filters, errors
from pyrogram.types import InputPhoneContact
from pyrogram.handlers import MessageHandler

from app.config.settings import _config
from app.lang import _lang



class TGCli(object):

    def __init__(self, *args, **kwargs):
        self.cliapp = Client(_config.cliSession, _config.cliApiId, _config.cliApiHash)
        self.cliapp.start()
        self.cliapp.add_handler(MessageHandler(self.who_am_i, filters.command("me", '!')))
        self.CONTACTS = self.cliapp.get_contacts()

    def stop(self):
        self.cliapp.stop()

    def who_am_i(self, client, message):
        logging.info('Recieve command "me" message from user({0}) Phone:{1} Name: {3} {2} Username:{4}'.format(message.from_user.id, message.from_user.phone_number,
                    message.from_user.last_name, message.from_user.first_name, message.from_user.username))
        client.send_message(message.from_user.id, '{}: {}'.format(_lang.get('m_who_am_i') ,message.from_user.id))


    async def sendMsg(self, phone, msg):
        try:
            contact = await self.get_or_create_contact(phone)
            await self.cliapp.send_message(contact.id, msg) #TODO: Подумать над очередью если поймали флуд.
        except errors.FloodWait as e:
            time.sleep(e.x)

    async def get_or_create_contact(self, phone):
        for contact in self.CONTACTS:
            if contact.phone_number in phone:
                return contact
        contact = await self.cliapp.import_contacts([InputPhoneContact(phone, phone),])
        self.CONTACTS.append(contact.users[0])
        return contact.users[0]



cliWorker = TGCli()