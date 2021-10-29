# -*- coding: utf-8 -*-
import logging
import datetime

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

from app.config.settings import _config
from app.tgbot.admin import *

class TGBot(object):
    def __init__(self, *args, **kwargs):
        logging.basicConfig(format="%(asctime)s %(levelname)s\t%(name)s:%(message)s", level= _config.logLevel)
        logging.getLogger("telegram.bot").setLevel(_config.logLevel)
        self.updater = Updater(_config.botToken)

    def regHandler(self):
        self.updater.dispatcher.add_handler(CommandHandler('start', self.hello))
        self.updater.dispatcher.add_handler(CommandHandler('token', generate_token))


    def error(self, bot, update, error):
        logging.warning('Update "%s" caused error "%s"' % (update, error))

    def start(self):
        self.updater.start_polling()
        #self.updater.idle()

    def stop(self):
        self.updater.stop()

    def status(self):
        return self.updater.is_idle

    def sendMsg(self, chat, msg, parse_mode = "HTML", dis_web_preview = True, dis_notify = False):
        msgs = self.breakLongMessage(msg)
        for mess in msgs:
            sofg = self.updater.bot.sendMessage(chat, text=mess, parse_mode = parse_mode,
                                         disable_notification = dis_notify, disable_web_page_preview = dis_web_preview)

    def hello(self, bot, update):
        bot.sendMessage(update.message.chat_id,
                            text='Добрый день. Данный бот подключен к системе оповещений. Для получения доступа к нотификации, напишите вашему админу')

    def breakLongMessage(self, msg, max_len = 4096):
        result = []
        lines = msg.split("\n")
        line = lines.pop(0)
        msgpartLen = 0
        msgpart = []
        while True:
          if msgpartLen + len(line) >= max_len:
            result.append("\n".join(msgpart))
            msgpartLen = len(line) + 1
            msgpart = [line]
          else:
            msgpartLen += len(line) + 1
            msgpart.append(line)
          if len(lines) > 0:
            line = lines.pop(0)
          else:
            break

        result.append("\n".join(msgpart))
        return result 

worker = TGBot()