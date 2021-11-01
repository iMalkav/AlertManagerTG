# -*- coding: utf-8 -*-
import logging
import datetime

from pyrogram import Client, filters
from pyrogram.types import InputPhoneContact

from app.config.settings import _config



class TGCli(object):
    
    def __init__(self, *args, **kwargs):
        self.cliapp = Client(_config.cliSession, _config.cliApiId, _config.cliApiHash)

    async def sendMsg(self, phone, msg):
        async with self.cliapp:
            contact = await self.get_or_create_contact(phone)
            await self.cliapp.send_message(contact.id, msg)



    async def get_or_create_contact(self, phone):
        contacts = await self.cliapp.get_contacts()
        for contact in contacts:
            if contact.phone_number in phone:
                return contact
        contact = await self.cliapp.import_contacts([InputPhoneContact(phone, phone),])
        return contact.users[0]
        


cliWorker = TGCli()