import os
import sys
import logging
import xml.etree.ElementTree as et

from app.config.settings import _config


class Lang(object):

    def __init__(self, base_path=None):
        try:
            main_script_path = sys.argv[0]
            main_script_dir = os.path.dirname(
                os.path.abspath(main_script_path))

            file_path = os.path.join(
                main_script_dir, 'locales', '{}.xml'.format(_config.lang))
            # file_path = os.path.abspath('locales/{}.xml'.format(_config.lang))
            logging.info('Load lang "{}"'.format(_config.lang))
            self.tree = et.parse(file_path).getroot()
        except:
            logging.info(
                'Fail load lang "{}", load default "ru-RU"'.format(_config.lang))
            file_path = os.path.abspath(
                'locales/ru-RU.xml'.format(_config.lang))
            self.tree = et.parse(file_path).getroot()

    def get(self, key):
        text = self.tree.find('.//String[@key="{}"]'.format(key)).text
        if text is None:
            return '{}(Not found text)'.format(key)
        return text
