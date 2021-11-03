import os
import logging
import xml.etree.ElementTree as et

from app.config.settings import _config

class Lang(object):

    def __init__(self, *args, **kwargs):
        try:
            logging.info('Load lang "{}"'.format(_config.lang))
            self.tree = et.parse('locales\{}.xml'.format(_config.lang)).getroot()
        except:
            logging.info('Fail load lang "{}", load default "ru-RU"'.format(_config.lang))
            self.tree = et.parse('locales\\ru-RU.xml').getroot()

        
    def get(self, key):
        text = self.tree.find('.//String[@key="{}"]'.format(key)).text
        if text is None:
            return '{}(Not found text)'.format(key)
        return text
        


_lang = Lang()