# -*- coding: utf-8 -*-
from app.tgbot.ACLCheck import ACLCheck
import uuid

@ACLCheck("admin")
def generate_token(bot, update):
    user = UserBase(token = str(uuid.uuid4()))
    user.save()
    bot.sendMessage(update.message.chat_id,
                            text='Токен сформирован: ' + user.token)
    


