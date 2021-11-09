import os
import logging
import xml.etree.ElementTree as et

from app.config.settings import _config

class Lang(object):

    def __init__(self, *args, **kwargs):
        try:
            file_path = os.path.abspath('locales/{}.xml'.format(_config.lang))
            logging.info('Load lang "{}"'.format(_config.lang))
            self.tree = et.parse(file_path).getroot()
        except:
            logging.info('Fail load lang "{}", load default "ru-RU"'.format(_config.lang))
            file_path = os.path.abspath('locales/ru-RU.xml'.format(_config.lang))
            self.tree = et.parse(file_path).getroot()

        
    def get(self, key):
        text = self.tree.find('.//String[@key="{}"]'.format(key)).text
        if text is None:
            return '{}(Not found text)'.format(key)
        return text
        


